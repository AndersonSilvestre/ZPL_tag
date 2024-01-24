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
import requests
import shutil
import csv
import os
import sys
import PyPDF2

# app = Tk()  # instancia o app
# app.geometry('500x150')  # tamanho da tela
# app.title("Etiquetas")  # Nome da aba aberta

# archive path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'base_produtos.csv')


class Aplicativo(tk.Tk):
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('500x200')
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        self.frames = {}

        for F in (TelaPrincipal, Adiciona):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(TelaPrincipal)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class TelaPrincipal(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.quant_etiquetas = IntVar()
        self.cod_int = StringVar()
        self.resultString = StringVar()
        self.numPedido = StringVar()
        self.nomePdf = StringVar()
        self.pdfs = []
        self.modelo_etiqueta_mm = [
            [20, 35], [30, 75], [50, 105]
        ]

        # Labels
        ttk.Label(self, text="Insira o Cod do produto").grid(column=0, row=1, padx=5, pady=5)
        ttk.Label(self, text="Insira a Quant de etiquetas").grid(column=0, row=2, padx=5, pady=5)
        ttk.Label(self, text="Insira o Numero do pedido").grid(column=0, row=3, padx=5, pady=5)

        # Entrys
        self.codigo = tk.Entry(self, textvariable=self.cod_int)
        self.codigo.grid(column=1, row=1, padx=5, pady=5)
        self.etiqueta = tk.Entry(self, textvariable=self.quant_etiquetas)
        self.etiqueta.grid(column=1, row=2, padx=5, pady=5)
        ttk.Entry(self, textvariable=self.numPedido).grid(column=1, row=3)

        # buttons
        # tk.Frame(self, width=500, height=80, borderwidth=2, relief="groove").grid(column=0, row=4, columnspan=10, sticky='nsew')
        ttk.Button(self, text="Gera Etiquetas", command=self.existe_prod).grid(column=0, row=4, padx=0, pady=10)
        self.btn_sair = ttk.Button(self, text="Sair", command=self.quit)
        self.btn_sair.grid(column=1, row=4, padx=3, pady=0)
        ttk.Button(self, text="Finalizar PDF", command=self.merge).grid(column=2, row=4, padx=0, pady=10)
        ttk.Button(self, text="Adiciona Item", command=lambda: controller.show_frame(Adiciona))\
            .grid(column=1, row=5, padx=0, pady=1)
        
    def limpa(self,cod,eti):
        entries = (cod,eti)
        for entry in entries:
            entry.delete(0, tk.END)
        self.btn_sair.destroy()

    def lista_pdf(self):
        # Nomeia e gera a lista de pdfs
        self.nomePdf.set("item" + self.cod_int.get().upper() + "-" + self.numPedido.get() + ".pdf")
        self.pdfs.append(self.nomePdf.get())
        return self.pdfs

    def existe_prod(self):
        # Verifica se o Produto existe e se foi digitado alguma quantidade de etiquetas e pedido.
        desc = self.busca_produto(self.cod_int.get().upper())
        if desc is not None:
            if self.quant_etiquetas.get() >= 1:
                if self.numPedido.get() != "":
                    self.gera_pdf()
                else:
                    messagebox.showinfo("Pedido", "Favor inserir número do pedido")
            else:
                messagebox.showinfo("Etiquetas", "Favor inserir quantidade de etiquetas!")
        else:
            messagebox.showinfo("Não encontrado", "Produto não encontrado")

    def gera_pdf(self):
        #  parametros de execucao
        modelo = 1

        self.lista_pdf()
        zpl = self.cria_zpl(self.cod_int.get().upper(), self.quant_etiquetas.get(), modelo)

        print("ZPL completo.")
       
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
                aksbox = messagebox.askquestion("Nova Etiqueta", "Gostaria de incluir mais produtos?")
            if aksbox == 'yes':
                pass
            else:
                self.merge()
        else:
            print('Error: ' + response.text)
        self.limpa(self.codigo, self.etiqueta)

    

    def cria_linha(self, p_qtd_etiqueta, p_cod_produto, p_linhas):
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

        desc = ""

        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                #  se encontra código retorna valores
                if row[0] == str(p_cod_produto):
                    desc = row[1]
                    cod_barra = row[2]

        if desc != "":
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
        messagebox.showinfo("PDF", "PDF Gerado")
        self.quit()


class Adiciona(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Variaveis
        self.cod = StringVar()
        self.ean = StringVar()
        self.nome = StringVar()

        tk.Label(self, text="Digite o Codigo").grid(column=1, row=1)
        tk.Label(self, text="Digite o Nome\ndo Produto").grid(column=1, row=2)
        tk.Label(self, text="Digite os 12 digitos\ndo Codigo EAN").grid(column=1, row=3)

        self.codigo = tk.Entry(self, textvariable=self.cod)
        self.codigo.grid(column=2, row=1, columnspan=1)
        self.nome = tk.Entry(self, textvariable=self.nome)
        self.nome.grid(column=2, row=2, columnspan=1)
        self.ean = tk.Entry(self, textvariable=self.ean)
        self.ean.grid(column=2, row=3, columnspan=1)

        tk.Button(self, text="Verificar", command=self.calcula).grid(column=1, row=4)
        # tk.Button(self, text="quit", command=self.destroy).grid(column=3, row=4)
        tk.Button(self, text="Voltar", command=lambda: controller.show_frame(TelaPrincipal)).grid(column=3, row=4)
        # tk.Button(self, text="Cria Linha", command=self.cria_linha).grid(column=2, row=4)

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
        self.lista = list(self.ean.get())
        descricao = self.busca_produto(self.codigo.get().upper())
        if descricao != None:
            messagebox.showinfo('Já existe', 'Material já cadastrado')
        else:
            if len(self.lista) <= 11 or len(self.lista) >= 13:
                print('Nao tem 12')
                messagebox.showinfo('Código', 'Inserir 12 digitos p/ o calculo')
            else:

                #print(self.linha)
                tk.Button(self, text="Cria Linha", command=self.cria_linha).grid(column=2, row=4)

    def cria_linha(self):
        total = 0
        if self.cod.get() == '':
            messagebox.showinfo('Cod', 'Inserir Codigo do material')
        elif self.nome.get() == '':
            messagebox.showinfo('Nome', 'Inserir Nome do material')

        elif len(self.lista) <= 11 or len(self.lista) >= 13:
            messagebox.showinfo('Código', 'Inserir 12 digitos p/ o calculo')
        else:
            self.calcula()
            for idx, i in enumerate(self.lista):
                if int(idx) % 2 == 0:
                    total += int(i)
                else:
                    total += int(i) * 3
            self.lista.append((10 - (total % 10)) % 10)
            lista = ''.join(str(i) for i in self.lista)
            print(lista)
            linha = self.cod.get() + ',' + self.nome.get() + ',' + str(lista) + '\n'
            print(linha)
            with open('tst_input.txt', 'a') as arquivo:
                arquivo.write(linha)
                self.limpa()
            messagebox.showinfo("Item", "Item Gravado")


app = Aplicativo()
app.mainloop()