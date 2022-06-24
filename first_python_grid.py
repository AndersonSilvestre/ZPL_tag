'''
	Referencias 
	https://www.delftstack.com/pt/tutorial/tkinter-tutorial/tkinter-entry/
'''

from tkinter import *
from tkinter import ttk



app = Tk() #instancia o app
app.geometry('300x200') #tamanho da tela
frm = ttk.Frame(app, padding=20)

def callbackFunc():
	resultString.set(codInt.get())
	print(codInt.get())

#frm.pack()
#ttk.Button(frm, text="teste botao")#.grid(column=1, row=1)

textEx = ttk.Label(app, text="Hello World!")
resultString= StringVar()
resultLabel = ttk.Label(app, textvariable=resultString)
codInt = StringVar()
entryCod = ttk.Entry(app, textvariable=codInt)

#botoes
btnShow = ttk.Button(app, text="show", command=callbackFunc)
btnQuit = ttk.Button(app, text="Quit", command=app.destroy)#.grid(column=1, row=0)


#Chamada dos widgets
textEx.pack() #'chama' a variavel de texto
resultLabel.pack()
entryCod.pack()
btnShow.pack(side = "left")
#btnQuit.pack(side  = "left") #'chama' a variavel botao



app.mainloop()