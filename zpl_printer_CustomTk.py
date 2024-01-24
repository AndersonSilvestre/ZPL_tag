# coding: utf-8
"""
    Referencias
    https://www.delftstack.com/pt/tutorial/tkinter-tutorial/tkinter-entry/
    https://stackoverflow.com/questions/3444645/merge-pdf-files
    https://pt.stackoverflow.com/questions/319195/transi%C3%A7%C3%A3o-de-telas-tkinter
"""

from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename
from ctypes import cast
import requests
import shutil
import csv
import os
import sys
import PyPDF2

import customtkinter

# app = Tk()  # instancia o app
# app.geometry('500x150')  # tamanho da tela
# app.title("Etiquetas")  # Nome da aba aberta

# archive path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'base_produtos.csv')


class TelaPrincipal(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.quant_etiquetas = IntVar()
        self.cod_int = StringVar()
        self.resultString = StringVar()
        self.numPedido = StringVar()
        self.nomePdf = StringVar()
        self.pdfs = []
        self.topo = None
        self.modelo_etiqueta_mm = [
            [20, 35], [30, 75], [50, 105]
        ]

        # Labels
        customtkinter.CTkLabel(self, text="Insira o Cod do produto").grid(column=0, row=1, padx=5, pady=5)
        customtkinter.CTkLabel(self, text="Insira a Quant de etiquetas").grid(column=0, row=2, padx=5, pady=5)
        customtkinter.CTkLabel(self, text="Insira o Numero do pedido").grid(column=0, row=3, padx=5, pady=5)

        # Entrys
        customtkinter.CTkEntry(self, textvariable=self.cod_int).grid(column=1, row=1, padx=5, pady=5)
        customtkinter.CTkEntry(self, textvariable=self.quant_etiquetas).grid(column=1, row=2, padx=5, pady=5)
        customtkinter.CTkEntry(self, textvariable=self.numPedido).grid(column=1, row=3)

        # buttons
        # tk.Frame(self, width=500, height=80, borderwidth=2, relief="groove").grid(column=0, row=4, columnspan=10, sticky='nsew')
        customtkinter.CTkButton(self, text="Gera Etiquetas", command=self.existe_prod).grid(column=0, row=4, padx=0, pady=10)
        customtkinter.CTkButton(self, text="Sair", command=self.quit).grid(column=1, row=4, padx=3, pady=0)
        customtkinter.CTkButton(self, text="Finalizar PDF", command=self.merge).grid(column=2, row=4, padx=0, pady=10)
        customtkinter.CTkButton(self, text="Adiciona Item", command=self.abre_adiciona).grid(column=1, row=5, padx=0, pady=1)
        
    # Abertura das telas de Alerta
     
    def abre_adiciona(self):
        if self.topo is None or not self.topo.winfo_exists():
            self.topo = Adiciona(self)  # create window if its None or destroyed
        else:
            self.topo.focus()  # if window exists focus it

    def abre_n_encontrado(self):
        if self.topo is None or not self.topo.winfo_exists():
            self.topo = ProdNaoEncontrado(self)
        else:
            self.topo.focus()
    
    def inserir_etiqueta(self):
        if self.topo is None or not self.topo.winfo_exists():
            self.topo = InserirEtiquetas(self)
        else:
            self.topo.focus()
    
    def num_pedido(self):
        if self.topo is None or not self.topo.winfo_exists():
            self.topo = NumeroPedido(self)
        else:
            self.topo.focus()

    def lista_pdf(self):
        # Nomeia e gera a lista de pdfs
        self.nomePdf.set("item" + self.cod_int.get().upper() + "-" + self.numPedido.get() + ".pdf")
        self.pdfs.append(self.nomePdf.get())
        return self.pdfs
    
    # Fim das telas de alarme

    def existe_prod(self):
        # Verifica se o Produto existe e se foi digitado alguma quantidade de etiquetas e pedido.
        desc = self.busca_produto(self.cod_int.get().upper())
        if desc is not None:
            if self.quant_etiquetas.get() >= 1 or self.quant_etiquetas.get() == None:
                if self.numPedido.get() != "":
                    self.gera_pdf()
                else:
                    self.num_pedido()
            else:
                self.inserir_etiqueta()
        else:
            self.abre_n_encontrado()

    def gera_pdf(self):
        #  parametros de execucao
        modelo = 1

        self.lista_pdf()
        zpl = self.cria_zpl(self.cod_int.get().upper(), self.quant_etiquetas.get(), modelo)

        print("ZPL completo.")
        #  print(zpl)

        #  Configuração do POST
        largura_inches = 4
        altura_inches = 0.78
        url_alterada = 'http://api.labelary.com/v1/printers/8dpmm/labels/' + str(largura_inches) + 'x' + str(
            altura_inches) + '/+' + str(self.quant_etiquetas) + '/'
        files = {'file': zpl}
        headers = {'Accept': 'application/pdf'}  # omit this line to get PNG images back
        response = requests.post(url_alterada, headers=headers, files=files, stream=True)

        #  Tratamento da resposta do POST
        if response.status_code == 200:
            response.raw.decode_content = True
            with open(self.nomePdf.get(), 'wb') as out_file:  # change file name for PNG images
                shutil.copyfileobj(response.raw, out_file)
                NovaEtiqueta(self)
            '''    
                aksbox = messagebox.askquestion("Nova Etiqueta", "Gostaria de incluir mais produtos?")
            if aksbox == 'yes':
                pass
            else:
                self.merge()
            '''
        else:
            print('Error: ' + response.text)

    def cria_linha(self, p_qtd_etiqueta, p_cod_produto, p_linhas):
        #  Função
        #  "Uma linha de etiquetas, com a logica de colocar menos etiquetas."
        #  Funciona apenas para o modelo especifico de 3 etiquetas por hora

        zpl_linha = ""

        #  inicio
        zpl_linha += "^XA"

        #  Busca informações de produto
        produto_desc, produto_cod_barras = self.busca_produto(p_cod_produto)

        print("Inicio linha, etiquetas: " + str(p_qtd_etiqueta))

        #  gera etiquetas
        if p_qtd_etiqueta - 3 >= 0:
            #  linha completa com 3 etiquetas
            zpl_linha += self.cria_etiqueta(20, 3, produto_desc, produto_cod_barras)
            zpl_linha += self.cria_etiqueta(290, 3, produto_desc, produto_cod_barras)
            zpl_linha += self.cria_etiqueta(570, 3, produto_desc, produto_cod_barras)
        # print("linha completa")
        elif p_qtd_etiqueta - 3 == -1:
            #  final com 2 etiquetas
            zpl_linha += self.cria_etiqueta(20, 10, produto_desc, produto_cod_barras)
            zpl_linha += self.cria_etiqueta(290, 10, produto_desc, produto_cod_barras)
        # print("linha 2 etiqueta")
        else:
            #  final com 1 etiqueta
            zpl_linha += self.cria_etiqueta(20, 10, produto_desc, produto_cod_barras)
        # print("linha 1 etiqueta")

        # fim
        zpl_linha += "^XZ"

        return zpl_linha

    def cria_etiqueta(self, pos_coluna, pos_linha, produto, cod_barra):
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

    def busca_produto(self, p_cod_produto):
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

    def cria_zpl(self, p_cod_produto, p_qtd_etiqueta, p_modelo_etiqueta):
        """
        Função que gera o texto completo do ZPL.
        """
        pre_zpl = ""
        loop_etiqueta = p_qtd_etiqueta
        linhas = 1

        #  loop para gerar linhas
        while loop_etiqueta > 0:
            pre_zpl += self.cria_linha(loop_etiqueta, p_cod_produto, linhas)
            linhas += 1
            loop_etiqueta -= 3
        return pre_zpl

    def merge(self):
        """
        Função para agrupar os pdf's na finalização dos programas
        """
        merger = PyPDF2.PdfMerger()

        for pdf in self.pdfs:
            merger.append(pdf)
        merger.write("Pedido - " + self.numPedido.get() + ".pdf")
        merger.close()
        os.system("find -type f -name 'item*' -delete")
        PdfGerado(self)


class Adiciona(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Variaveis
        self.cod = StringVar()
        self.ean = StringVar()
        self.nome = StringVar()
        # self.verificador = 0

        customtkinter.CTkLabel(self, text="Digite o Codigo").grid(column=1, row=1)
        customtkinter.CTkLabel(self, text="Digite o Nome\ndo Produto").grid(column=1, row=2)
        customtkinter.CTkLabel(self, text="Digite os 12 digitos\ndo Codigo EAN").grid(column=1, row=3)

        self.codigo = customtkinter.CTkEntry(self, textvariable=self.cod)
        self.codigo.grid(column=2, row=1, columnspan=1)
        self.nome = customtkinter.CTkEntry(self, textvariable=self.nome)
        self.nome.grid(column=2, row=2, columnspan=1)
        self.ean = customtkinter.CTkEntry(self, textvariable=self.ean)
        self.ean.grid(column=2, row=3, columnspan=1)

        customtkinter.CTkButton(self, text="Verificar", command=self.calcula).grid(column=1, row=4)
        # customtkinter.CTkButton(self, text="quit", command=self.destroy).grid(column=3, row=4)
        customtkinter.CTkButton(self, text="Voltar", command=self.destroy).grid(column=3, row=4)
        # customtkinter.CTkButton(self, text="Cria Linha", command=self.cria_linha).grid(column=2, row=4)

    def limpa(self):
        entries = (self.codigo, self.nome, self.ean)
        for entry in entries:
            entry.delete(0, tk.END)

    def busca_produto(self, p_cod_produto):
        desc = ""

        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                #  se encontra código retorna valores
                if row[0] == str(p_cod_produto):
                    desc = row[1]

        if desc != "":
            # print(p_cod_produto, desc, cod_barra)
            print("Produto já existe")
            return desc


    def calcula(self):
        total = 0
        self.lista = list(self.ean.get())
        descricao = self.busca_produto(self.codigo.get().upper())
        if descricao != None:
            messagebox.showinfo('Já existe', 'Material já cadastrado')
        else:
            if len(self.lista) <= 11 or len(self.lista) >= 13:
                print('Nao tem 12')
                messagebox.showinfo('Código', 'Inserir 12 digitos p/ o calculo')
            else:
                for idx, i in enumerate(self.lista):
                    #print(idx, i)
                    if int(idx) % 2 == 0:
                        total += int(i)
                    else:
                        total += int(i) * 3

                self.lista.append((10 - (total % 10)) % 10)
                lista = ''.join(str(i) for i in self.lista)
                print(lista)
                #print(self.linha)
                customtkinter.CTkButton(self, text="Cria Linha", command=self.cria_linha).grid(column=2, row=4)

    def cria_linha(self):
        if self.cod.get() == '':
            messagebox.showinfo('Cod', 'Inserir Codigo do material')
        elif self.nome.get() == '':
            messagebox.showinfo('Nome', 'Inserir Nome do material')

        elif len(self.lista) <= 11 or len(self.lista) >= 13:
            messagebox.showinfo('Código', 'Inserir 12 digitos p/ o calculo')
        else:
            self.calcula()
            linha = self.cod.get() + ',' + self.nome.get() + ',' + str(self.lista) + '\n'
            with open('tst_input.txt', 'a') as arquivo:
                arquivo.write(linha)
                self.limpa()
            messagebox.showinfo("Item", "Item Gravado")

# Telas de Alerta

class ProdNaoEncontrado(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("250x100")

        self.label = customtkinter.CTkLabel(self, text="Produto não encontrado")
        self.label.grid(column=1, row=1)
        self.quit = customtkinter.CTkButton(self, text='Voltar', command=self.destroy)
        self.quit.grid(column=1, row=2, pady=5, padx=5, sticky='nsew')

class InserirEtiquetas(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("250x150")

        self.label = customtkinter.CTkLabel(self, text="Inserir Etiquetas")
        self.label.grid(column=1, row=1)
        self.btn = customtkinter.CTkButton(self, text="Voltar", command= self.destroy)
        self.btn.grid(column=1, row=2)

class NumeroPedido(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("250x150")
        self.label = customtkinter.CTkLabel(self, text= "Insira o número do Pedido")
        self.label.grid(column=1, row=1)
        self.btn = customtkinter.CTkButton(self, text="Voltar", command=self.destroy)
        self.btn.grid(column=1, row=2)

class PdfGerado(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("250x150")
        self.title("PDF")
        self.label = customtkinter.CTkLabel(self, text= "PDF gerado")
        self.label.grid(column=1, row=1)
        self.btn = customtkinter.CTkButton(self, text="Voltar", command=self.quit)
        self.btn.grid(column=1, row=2)

class NovaEtiqueta(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("250x150")
        self.title("Nova Etiqueta")
        self.label = customtkinter.CTkLabel(self, text= "Nova Etiqueta")
        self.label.grid(column=1, row=1)
        self.btn = customtkinter.CTkButton(self, text="Sim", command=self.destroy)
        self.btn.grid(column=1, row=2)
        self.btn = customtkinter.CTkButton(self, text="Não", command=self.acrescenta)
        self.btn.grid(column=2, row=2)

    def acrescenta(self):
        TelaPrincipal.merge(self)
        PdfGerado(self)
        #self.quit()

app = TelaPrincipal()
app.mainloop()
