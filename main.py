import os
import openai

# Configuração do cliente OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')  # Recomenda-se usar variáveis de ambiente para segurança
if not openai_api_key:
    raise ValueError("A chave de API 'OPENAI_API_KEY' não foi encontrada. Defina a variável de ambiente corretamente. Consulte a documentação em https://platform.openai.com/account/api-keys para mais informações sobre como obter e configurar sua chave de API.")

openai.api_key = openai_api_key

# Diretório de onde o código irá buscar os arquivos
directory = '/Users/gabrielramos/Downloads/n8n-docs-main'

# Função para ler e categorizar os arquivos markdown
def categorizar_arquivos(diretorio):
    print(f"Iniciando a categorização dos arquivos no diretório: {diretorio}")
    if not os.path.exists(diretorio):
        raise FileNotFoundError(f"O diretório '{diretorio}' não foi encontrado.")
    
    arquivos_categorizados = []
    
    for root, _, files in os.walk(diretorio):
        for file in files:
            if file.endswith(".md"):  # Trabalha apenas com arquivos markdown
                file_path = os.path.join(root, file)
                print(f"Lendo o arquivo: {file_path}")
                
                # Lê o conteúdo do arquivo markdown
                with open(file_path, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Usa a OpenAI para categorizar e reparar o conteúdo
                categoria = categorizar_conteudo(conteudo)
                print(f"Categoria atribuída ao arquivo '{file}': {categoria}")
                reparado = reparar_markdown(conteudo)
                print(f"Arquivo '{file}' reparado com sucesso.")
                
                # Adiciona o conteúdo reparado e a categoria à lista
                arquivos_categorizados.append((categoria, reparado))
    
    if not arquivos_categorizados:
        print("Nenhum arquivo markdown encontrado no diretório especificado.")
        return ""

    # Ordena e concatena os conteúdos
    print("Ordenando os arquivos por categoria e concatenando o conteúdo.")
    arquivos_categorizados.sort(key=lambda x: x[0])
    conteudo_total = "\n\n".join([conteudo for _, conteudo in arquivos_categorizados])
    
    return conteudo_total

# Função para categorizar o conteúdo com a OpenAI
def categorizar_conteudo(conteudo):
    try:
        prompt = f"Identifique a categoria deste conteúdo markdown:\n\n{conteudo[:1000]}\n"
        print("Enviando solicitação para categorizar o conteúdo.")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        categoria = response.choices[0].message['content'].strip()
        print("Categoria recebida com sucesso.")
        return categoria
    except Exception as e:
        print(f"Erro ao categorizar conteúdo: {e}")
        return "Não categorizado"

# Função para reparar o markdown, se necessário
def reparar_markdown(conteudo):
    try:
        conteudos = [conteudo[i:i+4000] for i in range(0, len(conteudo), 4000)]
        reparado_completo = ""
        for index, chunk in enumerate(conteudos):
            prompt = f"Verifique e repare este conteúdo markdown para manter a estrutura correta e não apagar nenhuma informação:\n\n{chunk}\n"
            print(f"Enviando solicitação para reparar o conteúdo (chunk {index + 1} de {len(conteudos)}).")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            reparado = response.choices[0].message['content'].strip()
            print(f"Chunk {index + 1} reparado com sucesso.")
            reparado_completo += reparado + "\n"
        return reparado_completo.strip()
    except Exception as e:
        print(f"Erro ao reparar markdown: {e}")
        return conteudo

# Processamento dos arquivos e obtenção do conteúdo final
print("Iniciando o processamento dos arquivos markdown.")
conteudo_final = categorizar_arquivos(directory)

if conteudo_final:
    # Escreve o conteúdo final em um único arquivo markdown
    with open('concatenado.md', 'w', encoding='utf-8') as output_file:
        output_file.write(conteudo_final)

    print("Arquivos markdown processados e concatenados com sucesso em 'concatenado.md'.")
else:
    print("Não foi possível processar os arquivos markdown.")