'''
	Referencias 
	https://www.delftstack.com/pt/tutorial/tkinter-tutorial/tkinter-entry/
'''

from tkinter import *
from tkinter import ttk



app = Tk() #instancia o app
app.geometry('300x100') #tamanho da tela
frm = ttk.Frame(app, padding=20)

codInt = StringVar()
resultString= StringVar()
resultLabel = ttk.Label(app, textvariable=resultString)

def callbackFunc():
	resultString.set("{} - {}".format(codInt.get))

#frm.pack()
#ttk.Button(frm, text="teste botao")#.grid(column=1, row=1)

textEx = ttk.Label(app, text="Hello World!")
entryCod = ttk.Entry(app, textvariable=codInt)

#botoes
btnShow = ttk.Button(app, text="show", command=app.callbackFunc)
btnQuit = ttk.Button(app, text="Quit", command=app.destroy)#.grid(column=1, row=0)



textEx.pack() #'chama' a variavel de texto
entryCod.pack()
btnShow.pack()
btnQuit.pack() #'chama' a variavel botao



app.mainloop()