'''
	Referencias 
	https://www.delftstack.com/pt/tutorial/tkinter-tutorial/tkinter-entry/
    https://stackoverflow.com/questions/3444645/merge-pdf-files
    https://pt.stackoverflow.com/questions/319195/transi%C3%A7%C3%A3o-de-telas-tkinter
'''

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
import os

app = Tk() #instancia o app
app.geometry('500x200') #tamanho da tela
app.title("Etiquetas Petz")

#archive path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'base_produtos_andy.csv')
#vars
quantEtiquetas = IntVar()
codInt = StringVar()
resultString = StringVar()
numPedido = StringVar()
nomePdf = StringVar()
#convertStri = StringVar()
pdfs = []
#nomeProd = StringVar()
modelo_etiqueta_mm =[
    [20,35], [30,75], [50,105]
]


def callbackFunc():
	resultString.set("{} - {}".format(codInt.get(),quantEtiquetas.get()))
	print(codInt.get(), quantEtiquetas.get())

def lista_pdf():
    #nomeia e gera a lista de pdfs

    nomePdf.set("item"+codInt.get()+"-"+numPedido.get()+".pdf")
    print(nomePdf.get())
    pdfs.append(nomePdf.get())
    print(pdfs)
    return pdfs

def geraPdf():
    # parametros de execução
    modelo = 1
    #produto_cod = int(sys.argv[2])
    #etq_quantidade = int(sys.argv[3])

    desc=""

    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:

            # modificaar!!!

            # se encontra código retorna valores
            if row[0] == str(codInt.get()):
                desc=row[1]
    
        if desc != "":
            lista_pdf()
            if quantEtiquetas.get() < 1:
                messagebox.showinfo("Etiquetas","Favor inserir quantidade de etiquetas!")
                print("Favor digitar quantidade de etiquetas")

            else:

                zpl = cria_zpl(codInt.get(),quantEtiquetas.get(),modelo)
                
                print("ZPL completo.")
                # print(zpl)

                # Configuração do POST
                largura_inches=4
                altura_inches=0.78
                url_alterada = 'http://api.labelary.com/v1/printers/8dpmm/labels/'+str(largura_inches)+'x'+str(altura_inches)+'/+'+str(quantEtiquetas)+'/'
                files = {'file' : zpl}
                headers = {'Accept' : 'application/pdf'} # omit this line to get PNG images back
                response = requests.post(url_alterada, headers = headers, files = files, stream = True)

                # Tratamento da resposta do POST
                if response.status_code == 200:
                    response.raw.decode_content = True
                    with open(nomePdf.get(), 'wb') as out_file: # change file name for PNG images
                        shutil.copyfileobj(response.raw, out_file)
                    print(pdfs)                        
                    aksbox = messagebox.askquestion("nova","Gostaria de incluir mais produtos?")
                    if aksbox == 'yes':
                        pass
                    else:
                        merge()
                        messagebox.showinfo("PDF","PDF Gerado")
                        print("negou")
                        app.destroy()
                else:
                    print('Error: ' + response.text)

        else :
            messagebox.showinfo("Não encontrado","Produto não encontrado")

def cria_linha(p_qtd_etiqueta,p_cod_produto, p_linhas):
    # Função
    # "Uma linha de etiquetas, com a logica de colocar menos etiquetas."
    # Funciona apenas para o modelo especifico de 3 etiquetas por hora

    zpl_linha =""

    # inicio
    zpl_linha +="^XA"
    pos_inicial_x = 20 #caralha de linha
    pos_inicial_y = 10 
    passo_linha = 30

    # Busca informações de produto
    produto_desc,produto_cod_barras = busca_produto(p_cod_produto) 

    print("Inicio linha, etiquetas: "+str(p_qtd_etiqueta))

    # gera etiquetas
    if p_qtd_etiqueta -3 >= 0:
        # linha completa com 3 etiquetas
        zpl_linha += cria_etiqueta(20, 3, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(290, 3, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(570, 3, produto_desc, produto_cod_barras)
        print("linha completa")
    elif p_qtd_etiqueta -3 == -1:
        # final com 2 etiquetas
        zpl_linha += cria_etiqueta(20, 10, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(290, 10, produto_desc, produto_cod_barras)
        print("linha 2 etiqueta")
    else:
        # final com 1 etiqueta
        zpl_linha += cria_etiqueta(20, 10, produto_desc, produto_cod_barras)
        print("linha 1 etiqueta")

    #fim
    zpl_linha +="^XZ"

    return zpl_linha

def cria_etiqueta(pos_coluna, pos_linha, produto, cod_barra):
    # Função
    # Gera o ZPL para uma etiqueta.

    # string para concatenar
    etiqueta = ""

    #add encoding
    etiqueta+="^CI28"
    # inicio label
    etiqueta+='^LH'+str(pos_coluna)+','+str(pos_linha)    
    # bloco?
    etiqueta+='^FB205,2,2,C'   
    # nome do produto
    etiqueta+='^FO16,110,2^A0N,18,18^FD'+str(produto)+'\&^FS'   
    # codigo de barra
    etiqueta+='^FO30,15^BY2^BEN,55,Y,N'   
    # Cod de barras sem nº verificador 
    etiqueta+='^FX Cod de barras sem nº verificador'   
    # Codigo de Barras
    etiqueta+='^FD'+str(cod_barra)+'^FS'       
    # print quality 
    etiqueta+='^PQ1,0,1,Y'        

    return etiqueta  

def busca_produto(p_cod_produto):
    """
    Função para buscar info de produto
    """
    # path_file="base_produtos.csv"
    # path_file="etiquetas_zpl\\base_produtos.csv"

    desc=""

    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            # se encontra código retorna valores
            if row[0] == str(p_cod_produto):
                desc=row[1]
                cod_barra=row[2]
    
        if desc != "":
            #print(p_cod_produto, desc, cod_barra)
            return desc,cod_barra
        else :
            print("Código não encontrado")
            #sys.exit()

def cria_zpl(p_cod_produto, p_qtd_etiqueta, p_modelo_etiqueta):
    # Função
    # Gera texto completo do ZPL.

    pre_zpl=""
    loop_etiqueta = p_qtd_etiqueta
    linhas = 1

    # loop para gerar linhas
    while loop_etiqueta > 0:

        pre_zpl+=cria_linha(loop_etiqueta, p_cod_produto,linhas)

        linhas += 1
        loop_etiqueta -= 3
   
    return pre_zpl

def merge():
    #Função teste para agrupar os pdf's na finalização dos programas
    
    merger = PyPDF2.PdfFileMerger()
    #pdfs = []
    #merger = PdfMerger()
    print(pdfs)
    
    for pdf in pdfs:
        merger.append(pdf)
    merger.write(numPedido.get() + ".pdf")
    merger.close()
    os.system("find -type f -name 'item*' -delete")
    

#Labels
#nomeProg = ttk.Label(app, text="Etiquetas").grid(sticky='E')
etqText = ttk.Label(app, text="Insira o Cod do produto").grid(column=0, row=1, padx=5, pady=5)
quantText = ttk.Label(app, text="Insira a Quant de etiquetas").grid(column=0, row=2, padx=5, pady=5)
numPed = Label(app, text="Insira o Numero do pedido").grid(column=0, row=3, padx=5, pady=5)
resultLabel = ttk.Label(app, textvariable=resultString).grid(column=1, row=0)
#showNomeProd = ttk.Label(app, textvariable=nomeProd).grid(column=1, row=5)

#Entrys
entryCod = ttk.Entry(app, textvariable=codInt).grid(column=1, row=1, padx=5, pady=5)
entryqantEtiquetas = ttk.Entry(app, textvariable=quantEtiquetas).grid(column=1, row=2, padx=5, pady=5)
entryPedido = Entry(app, textvariable=numPedido).grid(column=1, row=3)

#buttons
btnQuit = ttk.Button(app, text="Sair", command=app.destroy).grid(column=1, row=4, padx=5, pady=10)
btnPdf = ttk.Button(app, text="Gera Etiquetas", command=geraPdf).grid(column=0, row=4, padx=5, pady=10)
#Button(app, text="show", command=merge).grid(column=0, row=3)
#btnProcura = ttk.Button(app, text="Procura csv", command=lambda: busca_produto(codInt.get())).grid(column=4, row=3)



app.mainloop()
