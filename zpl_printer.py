# coding: utf-8
"""
    Referencias
    https://www.delftstack.com/pt/tutorial/tkinter-tutorial/tkinter-entry/
    https://stackoverflow.com/questions/3444645/merge-pdf-files
    https://pt.stackoverflow.com/questions/319195/transi%C3%A7%C3%A3o-de-telas-tkinter
"""

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from ctypes import cast
import requests
import shutil
import csv
import os
import sys
import PyPDF2

app = Tk()  # instancia o app
app.geometry('500x150')  # tamanho da tela
app.title("Etiquetas")  # Nome da aba aberta

# archive path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'base_produtos.csv')
# Variaveis
quantEtiquetas = IntVar()
codInt = StringVar()
resultString = StringVar()
numPedido = StringVar()
nomePdf = StringVar()
pdfs = []
modelo_etiqueta_mm = [
    [20, 35], [30, 75], [50, 105]
]


def lista_pdf():
    # Nomeia e gera a lista de pdfs
    nomePdf.set("item" + codInt.get().upper() + "-" + numPedido.get() + ".pdf")
    pdfs.append(nomePdf.get())
    return pdfs


def existe_prod():
    # Verifica se o Produto existe e se foi digitado alguma quantidade de etiquetas e pedido.
    desc = busca_produto(codInt.get().upper())
    if desc is not None:
        if quantEtiquetas.get() >= 1:
            if numPedido.get() != "":
                geraPdf()
            else:
                messagebox.showinfo("Pedido", "Favor inserir número do pedido")
        else:
            messagebox.showinfo("Etiquetas", "Favor inserir quantidade de etiquetas!")
    else:
        messagebox.showinfo("Não encontrado", "Produto não encontrado")


def geraPdf():
    #  parametros de execucao
    modelo = 1

    lista_pdf()
    zpl = cria_zpl(codInt.get().upper(), quantEtiquetas.get(), modelo)

    print("ZPL completo.")
    #  print(zpl)

    #  Configuração do POST
    largura_inches = 4
    altura_inches = 0.78
    url_alterada = 'http://api.labelary.com/v1/printers/8dpmm/labels/' + str(largura_inches) + 'x' + str(
        altura_inches) + '/+' + str(quantEtiquetas) + '/'
    files = {'file': zpl}
    headers = {'Accept': 'application/pdf'}  # omit this line to get PNG images back
    response = requests.post(url_alterada, headers=headers, files=files, stream=True)

    #  Tratamento da resposta do POST
    if response.status_code == 200:
        response.raw.decode_content = True
        with open(nomePdf.get(), 'wb') as out_file:  # change file name for PNG images
            shutil.copyfileobj(response.raw, out_file)
            aksbox = messagebox.askquestion("Nova Etiqueta", "Gostaria de incluir mais produtos?")
        if aksbox == 'yes':
            pass
        else:
            merge()
    else:
        print('Error: ' + response.text)


def cria_linha(p_qtd_etiqueta, p_cod_produto, p_linhas):
    #  Função
    #  "Uma linha de etiquetas, com a logica de colocar menos etiquetas."
    #  Funciona apenas para o modelo especifico de 3 etiquetas por hora

    zpl_linha = ""

    #  inicio
    zpl_linha += "^XA"

    #  Busca informações de produto
    produto_desc, produto_cod_barras = busca_produto(p_cod_produto)

    print("Inicio linha, etiquetas: " + str(p_qtd_etiqueta))

    #  gera etiquetas
    if p_qtd_etiqueta - 3 >= 0:
        #  linha completa com 3 etiquetas
        zpl_linha += cria_etiqueta(20, 3, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(290, 3, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(570, 3, produto_desc, produto_cod_barras)
    # print("linha completa")
    elif p_qtd_etiqueta - 3 == -1:
        #  final com 2 etiquetas
        zpl_linha += cria_etiqueta(20, 10, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(290, 10, produto_desc, produto_cod_barras)
    # print("linha 2 etiqueta")
    else:
        #  final com 1 etiqueta
        zpl_linha += cria_etiqueta(20, 10, produto_desc, produto_cod_barras)
    # print("linha 1 etiqueta")

    # fim
    zpl_linha += "^XZ"

    return zpl_linha


def cria_etiqueta(pos_coluna, pos_linha, produto, cod_barra):
    """
    Função que gera o cod ZPL para uma etiqueta.
    """
    #  string para concatenar
    etiqueta = ""
    # adiciona encoding
    etiqueta += "^CI28"
    #  inicio da etiqueta
    etiqueta += '^LH' + str(pos_coluna) + ',' + str(pos_linha)
    #  bloco
    etiqueta += '^FB205,2,2,C'
    #  nome do produto
    etiqueta += '^FO16,110,2^A0N,18,18^FD' + str(produto) + '\&^FS'
    #  codigo de barra
    etiqueta += '^FO30,15^BY2^BEN,55,Y,N'
    #  Cod de barras EAN 13
    etiqueta += '^FX Cod de barras EAN 13'
    #  Codigo de Barras
    etiqueta += '^FD' + str(cod_barra) + '^FS'
    #  qualidade da impressao
    etiqueta += '^PQ1,0,1,Y'

    return etiqueta


def busca_produto(p_cod_produto):
    """
    Função para buscar info de produto
    """
    #  path_file="base_produtos.csv"
    #  path_file="etiquetas_zpl\\base_produtos.csv"

    desc = ""

    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            #  se encontra código retorna valores
            if row[0] == str(p_cod_produto):
                desc = row[1]
                cod_barra = row[2]

    if desc != "":
        # print(p_cod_produto, desc, cod_barra)
        return desc, cod_barra
    else:
        print("Código não encontrado")


def cria_zpl(p_cod_produto, p_qtd_etiqueta, p_modelo_etiqueta):
    """
    Função que gera o texto completo do ZPL.
    """
    pre_zpl = ""
    loop_etiqueta = p_qtd_etiqueta
    linhas = 1

    #  loop para gerar linhas
    while loop_etiqueta > 0:
        pre_zpl += cria_linha(loop_etiqueta, p_cod_produto, linhas)
        linhas += 1
        loop_etiqueta -= 3
    return pre_zpl


def merge():
    """
    Função para agrupar os pdf's na finalização dos programas
    """
    merger = PyPDF2.PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)
    merger.write("Pedido - " + numPedido.get() + ".pdf")
    merger.close()
    os.system("find -type f -name 'item*' -delete")
    messagebox.showinfo("PDF", "PDF Gerado")
    app.destroy()


# Labels
ttk.Label(app, text="Insira o Cod do produto").grid(column=0, row=1, padx=5, pady=5)
ttk.Label(app, text="Insira a Quant de etiquetas").grid(column=0, row=2, padx=5, pady=5)
ttk.Label(app, text="Insira o Numero do pedido").grid(column=0, row=3, padx=5, pady=5)

# Entrys
ttk.Entry(app, textvariable=codInt).grid(column=1, row=1, padx=5, pady=5)
ttk.Entry(app, textvariable=quantEtiquetas).grid(column=1, row=2, padx=5, pady=5)
ttk.Entry(app, textvariable=numPedido).grid(column=1, row=3)

# buttons
ttk.Button(app, text="Gera Etiquetas", command=existe_prod).grid(column=0, row=4, padx=0, pady=10)
ttk.Button(app, text="Sair", command=app.destroy).grid(column=1, row=4, padx=0, pady=0)
ttk.Button(app, text="Finalizar PDF", command=merge).grid(column=2, row=4, padx=0, pady=10)

app.mainloop()
