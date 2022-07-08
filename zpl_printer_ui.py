'''
Created on 24 de jun de 2022

@author: user
'''
"""
API: http://labelary.com/service.html
criar exe python
 https://stackoverflow.com/questions/2933/create-a-directly-executable-cross-platform-gui-app-using-python
 https://towardsdatascience.com/how-to-easily-convert-a-python-script-to-an-executable-file-exe-4966e253c7e9
Link gDrive: https://drive.google.com/drive/folders/17A4s9QyjexXN5PVqsVr_6xl8Xgld8DGz?usp=sharing
"""

"""
Definição
--
Entrada:
1 produto, quantidade de etiquetas
- modelo de etiqueta único (3 etq, 20x35)
--
Saída:
Arquivo com etiquetas em PDF
--
Exemplo de execução por shell:
python3 zpl_printer.py (modelo) (cod_produto) (qtde etiquetas)
python3 zpl_printer.py 1 0123456789 5
"""
from tkinter import *
from tkinter import ttk
from ctypes import cast
import requests
import shutil
import sys
import csv
import os



# 1: 20 x 35 (3 etiquetas)
# 2: 30 x 105/2
# 3: 50 x 105 

# Variáveis globais
# se tivesse em orientação de objeto poderia ser colocado qaundo gera o objeto

# em mm
modelo_etiqueta_mm =[
    [20,35], [30,75], [50,105]
]

# em polegada
modelo_etiqueta_in =[
    [0.787402,1.37795], [1.1811,2.95276], [1.9685,4.13386]
]

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'base_produtos.csv')



def main_shell():
    # Script de execução no main quando executa por shell

    # parametros de execução
    modelo = int(sys.argv[1])
    produto_cod = int(sys.argv[2])
    etq_quantidade = int(sys.argv[3])
    
    # valores de etiquetas para o ZPL
    etq_largura = modelo_etiqueta_mm[modelo][0]
    etq_altura = modelo_etiqueta_mm[modelo][1]

    # valores de etiquetas para o POST
    post_largura = modelo_etiqueta_in[modelo][0]
    post_altura = modelo_etiqueta_in[modelo][1]

    zpl = cria_zpl(produto_cod,etq_quantidade,modelo_etiqueta_mm[0])

    print("ZPL completo.")
    # print(zpl)

    # Configuração do POST
    largura_inches=4
    altura_inches=1
    url_alterada = 'http://api.labelary.com/v1/printers/8dpmm/labels/'+str(largura_inches)+'x'+str(altura_inches)+'/+'+str(etq_quantidade)+'/'
    files = {'file' : zpl}
    headers = {'Accept' : 'application/pdf'} # omit this line to get PNG images back
    response = requests.post(url_alterada, headers = headers, files = files, stream = True)

    # Tratamento da resposta do POST
    if response.status_code == 200:
        response.raw.decode_content = True
        with open('output.pdf', 'wb') as out_file: # change file name for PNG images
            shutil.copyfileobj(response.raw, out_file)
    else:
        print('Error: ' + response.text)



quantEtiquetas = IntVar
codInt = IntVar
resultString= StringVar

def callbackFunc():
    resultString.set("{} - {}".format(codInt.get(),quantEtiquetas.get()))
    print(codInt.get(), quantEtiquetas.get())


def geraPdf():
    print("entrou aqui!")
    # parametros de execução
    modelo = 1
    #produto_cod = int(sys.argv[2])
    #etq_quantidade = int(sys.argv[3])

    zpl = cria_zpl(codInt.get(),quantEtiquetas.get(),modelo)

    print("ZPL completo.")
    # print(zpl)

    # Configuração do POST
    largura_inches=4
    altura_inches=1
    url_alterada = 'http://api.labelary.com/v1/printers/8dpmm/labels/'+str(largura_inches)+'x'+str(altura_inches)+'/+'+str(quantEtiquetas)+'/'
    files = {'file' : zpl}
    headers = {'Accept' : 'application/pdf'} # omit this line to get PNG images back
    response = requests.post(url_alterada, headers = headers, files = files, stream = True)

    # Tratamento da resposta do POST
    if response.status_code == 200:
        response.raw.decode_content = True
        with open('output.pdf', 'wb') as out_file: # change file name for PNG images
            shutil.copyfileobj(response.raw, out_file)
    else:
        print('Error: ' + response.text)



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
    etiqueta+='^FO16,115,2^A0N,18,18^FD '+str(produto)+' \&^FS'   
    # codigo de barra
    etiqueta+='^FO30,15^BY2^BEN,55,Y,N'   
    # Cod de barras sem nº verificador 
    etiqueta+='^FX Cod de barras sem nº verificador'   
    # Codigo de Barras
    etiqueta+='^FD '+str(cod_barra)+' ^FS'       
    # print quality 
    etiqueta+='^PQ1,0,1,Y'        

    print(etiqueta)
    return etiqueta    

def busca_produto(p_cod_produto):
    """
    Função para buscar info de produto
    """
    # path_file="base_produtos.csv"
    # path_file="etiquetas_zpl\\base_produtos.csv"

    desc=""

    print(p_cod_produto)

    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            # se encontra código retorna valores
            if row[0] == str(p_cod_produto):
                desc=row[1]
                cod_barra=row[2]
    
        if desc != "":
            return desc,cod_barra
        else :
            print("Código não encontrado")
            sys.exit()

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
        zpl_linha += cria_etiqueta(20, 10, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(290, 10, produto_desc, produto_cod_barras)
        zpl_linha += cria_etiqueta(570, 10, produto_desc, produto_cod_barras)
        print("linha compelta")
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


def main_ui():
    print("Add logicas do UI.")
    app = Tk() #instancia o app
    app.geometry('600x250') #tamanho da tela
    #vars

    #Labels
    nomeProg = ttk.Label(app, text="Etiquetas").grid(sticky='E')
    etqText = ttk.Label(app, text="Insira o Cod do produto").grid(column=0, row=1 )
    quantText = ttk.Label(app, text="Insira a Quant de etiquetas").grid(column=0, row=2)
    #resultLabel = ttk.Label(app, textvariable=resultString).grid(column=1, row=4)
    #showNomeProd = ttk.Label(app, textvariable=nomeProd).grid(column=1, row=5)

    #Entrys
    entryCod = ttk.Entry(app, textvariable=codInt).grid(column=1, row=1, padx=20, pady=20)
    entryqantEtiquetas = ttk.Entry(app, textvariable=quantEtiquetas).grid(column=1, row=2, padx=20, pady=20)

    #buttons
    btnShow = ttk.Button(app, text="show", command=lambda: callbackFunc).grid(column=0, row=3)
    btnQuit = ttk.Button(app, text="Quit", command=app.destroy).grid(column=1, row=3)
    #btnProcura = ttk.Button(app, text="Procura csv", command=lambda: busca_produto(codInt.get())).grid(column=4, row=3)
    btnPdf = ttk.Button(app, text="Gera Pdf", command=geraPdf).grid(column=2, row=3)

    app.mainloop()



# teste execução: 1 62008 7

if __name__ == '__main__':

    print(sys.argv)

    # separa a execução, se chamar com parametro é execução por shell
    if len(sys.argv) >= 2: # aqui fazes a verificacao sobre quantos args queres receber, o nome do programa conta como 1
        print('Execução de shell.')
        main_shell()
    else :
        print('Execução com Interface')
        main_ui()

    # encerra execução
    sys.exit()
