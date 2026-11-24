Jogo da Forca

Jogo da Forca com interface gráfica em Python (Tkinter). As palavras são lidas de um arquivo de texto, sorteadas a cada partida, e as estatísticas de vitórias e derrotas ficam salvas entre as execuções.

Funcionalidades
Palavra exibida com letras ocultas (_ _ _ _)
Teclado virtual A-Z (também funciona com o teclado físico)
Boneco da forca com 6 partes: cabeça, tronco, braço esquerdo, braço direito, perna esquerda e perna direita
Contador de tentativas restantes
Mensagens de vitória e derrota (na derrota a palavra é revelada)
Botões Novo Jogo, Desistir e Dica
Leitura de palavras de palavras.txt (59 palavras)
Seleção aleatória, sem repetir a palavra da partida anterior
Validação de letras já tentadas (o botão é desabilitado e a tecla repetida é ignorada)
Máximo de 6 erros
Estatísticas de vitórias, derrotas e total de partidas, salvas em estatisticas.json
Regras
Uma palavra é sorteada e mostrada com todas as letras ocultas.
A cada letra escolhida: se estiver na palavra, ela é revelada; se não estiver, uma parte do boneco é desenhada.
Você vence ao descobrir todas as letras antes de completar 6 erros.
Você perde ao chegar a 6 erros.
Dica: revela uma letra ainda oculta, mas custa 1 tentativa. Só é permitida 1 dica por partida e não pode ser usada se ela causaria a derrota.
Desistir encerra a partida, revela a palavra e conta como derrota.
Como executar
Requisitos: Python 3.8+ com Tkinter (já incluído na instalação padrão do Python no Windows e no macOS).

bash
git clone https://github.com/SEU_USUARIO/forca.git
cd forca
python forca_gui.py
No Linux (Debian/Ubuntu), se o Tkinter não estiver instalado:
bash
sudo apt install python3-tk
Estrutura do projeto
forca/
├── forca_gui.py        # código do jogo
├── palavras.txt        # lista de palavras (uma por linha)
├── estatisticas.json   # gerado automaticamente ao terminar a primeira partida
├── .gitignore
└── README.md
Principais funções de forca_gui.py
Função	                      Descrição
carregar_palavras(arquivo)	Lê o .txt, ignora linhas vazias, comentários (#), duplicatas e palavras com caracteres fora de A-Z
escolher_palavra(lista)	Sorteia uma palavra
atualizar_display(palavra, letras_tentadas)	Monta o texto com letras ocultas
desenhar_boneco(canvas, erros)	Desenha a forca e as partes do boneco conforme os erros
verificar_vitoria(palavra, letras_tentadas)	Informa se todas as letras foram descobertas
salvar_estatisticas(vitorias, derrotas)	Grava as estatísticas em JSON
main()	Carrega as palavras e inicia a interface
Formato do arquivo de palavras
Uma palavra por linha, sem espaços. Acentos são removidos automaticamente (coração vira CORACAO). Linhas começando com # são comentários.
casa
computador
universidade
Para adicionar palavras, basta incluir novas linhas em palavras.txt.
Tecnologias:
Python 3
Tkinter (biblioteca padrão)
Autor

Projeto desenvolvido como atividade acadêmica.
