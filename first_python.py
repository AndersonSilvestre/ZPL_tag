'''
	Referencias 
	https://www.delftstack.com/pt/tutorial/tkinter-tutorial/tkinter-entry/
'''

from tkinter import *
from tkinter import ttk
import csv
import os

app = Tk() #instancia o app
app.geometry('400x200') #tamanho da tela

def callbackFunc():
	resultString.set("{} - {}".format(codInt.get(),quantEtiquetas.get()))
	print(codInt.get(), quantEtiquetas.get())

def busca_produto(p_cod_produto):
    """
    Função para buscar info de produto
    """
    # path_file="base_produtos.csv"
    # path_file="etiquetas_zpl\\base_produtos.csv"

    desc=""
    p_cod_produto.set(codInt.get())
    print()

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
            #sys.exit()


#vars
p_cod_produto = StringVar()

resultString= StringVar()
quantEtiquetas = StringVar()
codInt = StringVar()
nomeProd = StringVar()
#archive path
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'base_produtos.csv')

#Labels
nomeProg = ttk.Label(app, text="Etiquetas").grid(sticky='E')
etqText = ttk.Label(app, text="Insira o Cod do produto").grid(column=0, row=1 )
quantText = ttk.Label(app, text="Insira a Quant de etiquetas").grid(column=0, row=2)
resultLabel = ttk.Label(app, textvariable=resultString).grid(column=1, row=4)
showNomeProd = ttk.Label(app, textvariable=nomeProd).grid(column=1, row=5)

#Entrys
entryCod = ttk.Entry(app, textvariable=codInt).grid(column=1, row=1, padx=20, pady=20)
entryqantEtiquetas = ttk.Entry(app, textvariable=quantEtiquetas).grid(column=1, row=2, padx=20, pady=20)

#buttons
btnShow = ttk.Button(app, text="show", command=callbackFunc).grid(column=0, row=3)
btnQuit = ttk.Button(app, text="Quit", command=app.destroy).grid(column=1, row=3)
btnProcura = ttk.Button(app, text="Procura csv", command=busca_produto).grid(column=2, row=3)

app.mainloop()