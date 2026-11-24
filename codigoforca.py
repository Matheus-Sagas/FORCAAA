"""Jogo da Forca com interface gráfica (Tkinter).

As palavras são lidas de palavras.txt (uma por linha), a palavra é sorteada
a cada partida e as estatísticas de vitórias/derrotas ficam salvas em
estatisticas.json.
"""

import json
import os
import random
import string
import tkinter as tk
import unicodedata
from tkinter import messagebox

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_PALAVRAS = os.path.join(PASTA, "palavras.txt")
ARQUIVO_ESTATISTICAS = os.path.join(PASTA, "estatisticas.json")
MAX_ERROS = 6
MAX_DICAS = 1

COR_FUNDO = "#f5f5f0"
COR_TEXTO = "#222222"
COR_ACERTO = "#7bc67b"
COR_ERRO = "#e57373"
COR_VITORIA = "#2e7d32"
COR_DERROTA = "#c62828"


# --------------------------------------------------------------------------
# Lógica do jogo
# --------------------------------------------------------------------------
def normalizar(texto):
    """Remove acentos e converte para maiúsculas (ex.: 'Coração' -> 'CORACAO')."""
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")
    return sem_acento.upper()


def carregar_palavras(arquivo):
    """Lê as palavras do arquivo .txt (uma por linha).

    Ignora linhas vazias, comentários (#), duplicatas e palavras que
    contenham algo além de letras A-Z. Retorna lista em maiúsculas.
    """
    palavras = []
    with open(arquivo, encoding="utf-8") as f:
        for linha in f:
            palavra = normalizar(linha.strip())
            if not palavra or palavra.startswith("#"):
                continue
            if all(c in string.ascii_uppercase for c in palavra) and palavra not in palavras:
                palavras.append(palavra)
    return palavras


def escolher_palavra(lista):
    """Sorteia uma palavra da lista."""
    return random.choice(lista)


def atualizar_display(palavra, letras_tentadas):
    """Monta o texto da palavra com letras ocultas, ex.: 'C _ S A'."""
    return " ".join(l if l in letras_tentadas else "_" for l in palavra)


def verificar_vitoria(palavra, letras_tentadas):
    """True se todas as letras da palavra já foram descobertas."""
    return all(l in letras_tentadas for l in palavra)


def carregar_estatisticas():
    """Lê (vitorias, derrotas) do arquivo JSON; (0, 0) se não existir."""
    try:
        with open(ARQUIVO_ESTATISTICAS, encoding="utf-8") as f:
            dados = json.load(f)
        return int(dados.get("vitorias", 0)), int(dados.get("derrotas", 0))
    except (OSError, ValueError, AttributeError):
        return 0, 0


def salvar_estatisticas(vitorias, derrotas):
    """Grava as estatísticas no arquivo JSON."""
    try:
        with open(ARQUIVO_ESTATISTICAS, "w", encoding="utf-8") as f:
            json.dump({"vitorias": vitorias, "derrotas": derrotas}, f)
    except OSError:
        pass  # não impede o jogo de continuar


# --------------------------------------------------------------------------
# Desenho do boneco
# --------------------------------------------------------------------------
def desenhar_boneco(canvas, erros, cor="#222222"):
    """Desenha a forca e as partes do boneco conforme o número de erros (0-6)."""
    canvas.delete("all")
    # Estrutura da forca (sempre visível)
    canvas.create_line(30, 280, 200, 280, width=4, fill="#6d4c41")
    canvas.create_line(60, 280, 60, 30, width=4, fill="#6d4c41")
    canvas.create_line(60, 30, 160, 30, width=4, fill="#6d4c41")
    canvas.create_line(160, 30, 160, 60, width=3, fill="#6d4c41")

    partes = [
        lambda: canvas.create_oval(140, 60, 180, 100, width=3, outline=cor),    # 1 cabeça
        lambda: canvas.create_line(160, 100, 160, 180, width=3, fill=cor),      # 2 tronco
        lambda: canvas.create_line(160, 115, 130, 155, width=3, fill=cor),      # 3 braço esq.
        lambda: canvas.create_line(160, 115, 190, 155, width=3, fill=cor),      # 4 braço dir.
        lambda: canvas.create_line(160, 180, 135, 230, width=3, fill=cor),      # 5 perna esq.
        lambda: canvas.create_line(160, 180, 185, 230, width=3, fill=cor),      # 6 perna dir.
    ]
    for desenhar in partes[:erros]:
        desenhar()


# --------------------------------------------------------------------------
# Interface gráfica
# --------------------------------------------------------------------------
class JogoForca:
    def __init__(self, root, palavras):
        self.root = root
        self.palavras = palavras
        self.vitorias, self.derrotas = carregar_estatisticas()

        self.palavra = ""
        self.letras_tentadas = set()
        self.erros = 0
        self.dicas_usadas = 0
        self.ativo = False
        self.ultima_palavra = None

        root.title("Jogo da Forca")
        root.configure(bg=COR_FUNDO)
        root.resizable(False, False)
        self._montar_interface()
        root.bind("<Key>", self._tecla_fisica)
        self.novo_jogo()

    # ---- construção da tela ----
    def _montar_interface(self):
        tk.Label(self.root, text="JOGO DA FORCA", font=("Helvetica", 20, "bold"),
                 bg=COR_FUNDO, fg=COR_TEXTO).grid(row=0, column=0, columnspan=2, pady=(12, 0))

        self.lbl_stats = tk.Label(self.root, font=("Helvetica", 11),
                                  bg=COR_FUNDO, fg=COR_TEXTO)
        self.lbl_stats.grid(row=1, column=0, columnspan=2, pady=(0, 6))

        self.canvas = tk.Canvas(self.root, width=240, height=300, bg="white",
                                highlightthickness=1, highlightbackground="#bbbbbb")
        self.canvas.grid(row=2, column=0, padx=14, pady=6)

        direita = tk.Frame(self.root, bg=COR_FUNDO)
        direita.grid(row=2, column=1, padx=14, pady=6)

        self.lbl_palavra = tk.Label(direita, font=("Courier", 26, "bold"),
                                    bg=COR_FUNDO, fg=COR_TEXTO)
        self.lbl_palavra.pack(pady=(4, 8))

        self.lbl_tentativas = tk.Label(direita, font=("Helvetica", 12),
                                       bg=COR_FUNDO, fg=COR_TEXTO)
        self.lbl_tentativas.pack()

        self.lbl_mensagem = tk.Label(direita, font=("Helvetica", 14, "bold"),
                                     bg=COR_FUNDO, fg=COR_TEXTO, height=2)
        self.lbl_mensagem.pack(pady=4)

        teclado = tk.Frame(direita, bg=COR_FUNDO)
        teclado.pack(pady=6)
        self.botoes = {}
        for i, letra in enumerate(string.ascii_uppercase):
            b = tk.Button(teclado, text=letra, width=3, font=("Helvetica", 12, "bold"),
                          command=lambda l=letra: self.tentar_letra(l))
            b.grid(row=i // 9, column=i % 9, padx=2, pady=2)
            self.botoes[letra] = b
        self.bg_botao = self.botoes["A"].cget("bg")

        barra = tk.Frame(self.root, bg=COR_FUNDO)
        barra.grid(row=3, column=0, columnspan=2, pady=(6, 14))
        self.btn_novo = tk.Button(barra, text="Novo Jogo", width=12, command=self.novo_jogo)
        self.btn_novo.pack(side="left", padx=6)
        self.btn_dica = tk.Button(barra, text="Dica", width=12, command=self.dar_dica)
        self.btn_dica.pack(side="left", padx=6)
        self.btn_desistir = tk.Button(barra, text="Desistir", width=12, command=self.desistir)
        self.btn_desistir.pack(side="left", padx=6)

    # ---- fluxo do jogo ----
    def novo_jogo(self):
        candidatas = [p for p in self.palavras if p != self.ultima_palavra] or self.palavras
        self.palavra = escolher_palavra(candidatas)
        self.ultima_palavra = self.palavra
        self.letras_tentadas = set()
        self.erros = 0
        self.dicas_usadas = 0
        self.ativo = True

        for b in self.botoes.values():
            b.config(state="normal", bg=self.bg_botao)
        self.lbl_mensagem.config(text="Escolha uma letra!", fg=COR_TEXTO)
        self._atualizar_tela()

    def tentar_letra(self, letra):
        if not self.ativo or letra in self.letras_tentadas:
            return  # validação: letra já tentada ou jogo encerrado
        self.letras_tentadas.add(letra)
        acertou = letra in self.palavra
        self.botoes[letra].config(state="disabled", bg=COR_ACERTO if acertou else COR_ERRO)
        if not acertou:
            self.erros += 1
        self._checar_fim()

    def dar_dica(self):
        if not self.ativo:
            return
        if self.dicas_usadas >= MAX_DICAS:
            self.lbl_mensagem.config(text="Você já usou sua dica!", fg=COR_DERROTA)
            return
        if self.erros >= MAX_ERROS - 1:
            self.lbl_mensagem.config(text="Sem tentativas para gastar\ncom dica!", fg=COR_DERROTA)
            return
        ocultas = [l for l in set(self.palavra) if l not in self.letras_tentadas]
        if not ocultas:
            return
        letra = random.choice(ocultas)
        self.dicas_usadas += 1
        self.letras_tentadas.add(letra)
        self.botoes[letra].config(state="disabled", bg=COR_ACERTO)
        self.erros += 1  # a dica custa uma tentativa
        self.lbl_mensagem.config(text=f"Dica: a palavra tem a letra {letra}\n(custou 1 tentativa)",
                                 fg=COR_TEXTO)
        self._atualizar_tela()
        if verificar_vitoria(self.palavra, self.letras_tentadas):
            self._checar_fim()

    def desistir(self):
        if not self.ativo:
            return
        if messagebox.askyesno("Desistir", "Tem certeza que deseja desistir desta partida?"):
            self._encerrar(venceu=False, desistiu=True)

    def _checar_fim(self):
        if verificar_vitoria(self.palavra, self.letras_tentadas):
            self._encerrar(venceu=True)
        elif self.erros >= MAX_ERROS:
            self._encerrar(venceu=False)
        else:
            self._atualizar_tela()

    def _encerrar(self, venceu, desistiu=False):
        self.ativo = False
        if venceu:
            self.vitorias += 1
            msg, cor = "🎉 Você venceu!", COR_VITORIA
        else:
            self.derrotas += 1
            msg = "Você desistiu!" if desistiu else "Você perdeu!"
            msg += f"\nA palavra era: {self.palavra}"
            cor = COR_DERROTA
        salvar_estatisticas(self.vitorias, self.derrotas)
        for b in self.botoes.values():
            b.config(state="disabled")
        self._atualizar_tela(revelar=not venceu)
        self.lbl_mensagem.config(text=msg, fg=cor)

    # ---- atualização visual ----
    def _atualizar_tela(self, revelar=False):
        letras = set(self.palavra) if revelar else self.letras_tentadas
        self.lbl_palavra.config(text=atualizar_display(self.palavra, letras))
        restantes = MAX_ERROS - self.erros
        self.lbl_tentativas.config(text=f"Tentativas restantes: {restantes} / {MAX_ERROS}")
        cor_boneco = COR_DERROTA if (not self.ativo and self.erros >= MAX_ERROS) else COR_TEXTO
        desenhar_boneco(self.canvas, self.erros, cor_boneco)
        total = self.vitorias + self.derrotas
        self.lbl_stats.config(
            text=f"Vitórias: {self.vitorias}   Derrotas: {self.derrotas}   Partidas: {total}")
        self.btn_dica.config(
            state="normal" if self.ativo and self.dicas_usadas < MAX_DICAS else "disabled")
        self.btn_desistir.config(state="normal" if self.ativo else "disabled")

    def _tecla_fisica(self, evento):
        letra = normalizar(evento.char) if evento.char else ""
        if len(letra) == 1 and letra in string.ascii_uppercase:
            self.tentar_letra(letra)


def main():
    root = tk.Tk()
    try:
        palavras = carregar_palavras(ARQUIVO_PALAVRAS)
    except OSError:
        messagebox.showerror("Erro", f"Não foi possível abrir:\n{ARQUIVO_PALAVRAS}")
        return
    if len(palavras) < 1:
        messagebox.showerror("Erro", "O arquivo palavras.txt não contém palavras válidas.")
        return
    JogoForca(root, palavras)
    root.mainloop()


if __name__ == "__main__":
    main()