'''
Created on 30 de jun de 2022

@author: AndersonSilvestre

refs:
https://www.pythontutorial.net/tkinter/tkinter-object-oriented-window/
https://python-textbok.readthedocs.io/en/1.0/Introduction_to_GUI_Programming.html
https://acervolima.com/python-configuracao-e-recuperacao-de-valores-da-variavel-tkinter/
'''

from tkinter import *
from tkinter import ttk

#from zpl_printer_test_object import geraPdf

resultString = IntVar
quantEtiquetas = 0
quantInt = 0
codInt = StringVar

class ProgGui:
	def __init__(self, master):
		self.master = master
		#super().__init__()
		
		

		master.title('Etiquetas')
		master.geometry('500x200')
		self.pad = ttk.Frame(app, padding=100)

		self.nomeProg = ttk.Label(app, text="Etiquetas").grid(sticky='E')
		self.etqTxt = ttk.Label(app, text="Insira o Cod do produto").grid(column=0, row=1 )
		self.quanTxt = ttk.Label(app, text="Insira a Quant de etiquetas").grid(column=0, row=2)

		self.entryCod = ttk.Entry(app, textvariable=codInt).grid(column=1, row=1, padx=20, pady=20)
		self.entryqantEtiquetas = ttk.Entry(app, textvariable=quantEtiquetas).grid(column=1, row=2, padx=20, pady=20)
		
		self.btnQuit = ttk.Button(app, text="Quit", command=app.destroy).grid(column=1, row=3)
		#self.btnPdf = ttk.Button(app, text="Gera Pdf", command=getEtq).grid(column=0, row=3)
		self.returnaBtn = Button(app, text="exporta dados", command=self.convertVar).grid(column=0, row=4)
	
	def convertVar(self):
		print(type(quantEtiquetas))
		print(quantEtiquetas.get())
		

		#return quantInt

	def callbackFunc(self):
		resultString.set("{} - {}".format(codInt.get(),quantEtiquetas.get()))
		print(resultString)


from zpl_printer_test_object import *

app = Tk()
tela = ProgGui(app)
app.mainloop()