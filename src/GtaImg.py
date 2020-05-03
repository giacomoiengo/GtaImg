import os
import img
import webbrowser
import tkinter.filedialog
import tkinter as tk
from   tkinter import ttk as tr

class Application:
    title    = 'GtaImg'
    usageUrl = 'https://giacomoiengo.github.io/2020/gtaimg-usage/'

    def __init__(self):
        self.__widgetSetup()
    
    def __widgetSetup(self):
        font    = ('Arial', 10, 'bold')
        font2   = ('Arial', 10, 'bold italic')

        window = tk.Tk()
        window.minsize(650,300)
        window.title(self.title)
        window.protocol('WM_DELETE_WINDOW', self.shutdown)

        style = tr.Style()
        style.configure('Treeview', font=font)
        style.configure('Treeview.Heading', font=font)

        menubar   = tk.Menu(window)
        filemenu  = tk.Menu(menubar, tearoff=0)
        editmenu  = tk.Menu(menubar, tearoff=0)
        helpmenu  = tk.Menu(menubar, tearoff=0)

        mainTopFrame = tk.Frame(window)
        mainBotFrame = tk.Frame(window)
        mainTreTopFrame = tk.Frame(mainTopFrame)
        mainEtyTopFrame = tk.Frame(mainTopFrame)
        mainLblBotFrame = tk.Frame(mainBotFrame, bg='#bbbbbb', border=1)
        mainPrgBotFrame = tk.Frame(mainBotFrame)


        treeTop = tr.Treeview   (mainTreTopFrame)
        scrlTop = tk.Scrollbar  (mainTreTopFrame)
        etryTop = tk.Entry      (mainEtyTopFrame, font=font)
        lbelBot = tk.Label      (mainLblBotFrame, text='{} ready.'.format(self.title), font=font2, anchor=tk.W)  
        prgsBot = tr.Progressbar(mainPrgBotFrame, orient='horizontal', length=300, mode='determinate')

        window.bind('<Key>', self.shortcutHandle)
        etryTop.bind('<KeyRelease-Return>', self.searchDentry)
        treeTop.configure(columns=(0,1), yscrollcommand=scrlTop.set)
        scrlTop.configure(command=treeTop.yview)
        treeTop.column(0)
        treeTop.column(1)
        treeTop.heading('#0', text='Name')
        treeTop.heading(0, text='Offset')
        treeTop.heading(1, text='Size')
            
        
        filemenu.add_command(label='{:16}'.format('Open'),      accelerator='Ctrl+O',       command=self.menuOpen)
        filemenu.add_command(label='{:16}'.format('Save'),      accelerator='Ctrl+S',       command=self.menuSave)
        filemenu.add_command(label='{:16}'.format('Save as'),   accelerator='Ctrl+Shift+S', command=self.menuSaveAs)
        filemenu.add_command(label='{:16}'.format('Close'),     accelerator='Ctrl+Q',       command=self.menuClose)
        filemenu.add_separator()
        filemenu.add_command(label='{:16}'.format('Exit'),      accelerator='Alt+F4',       command=self.shutdown)
        editmenu.add_command(label='{:16}'.format('Extract'),   accelerator='Ctrl+E',       command=self.menuExtract)
        editmenu.add_command(label='{:16}'.format('Replace'),   accelerator='Ctrl+R',       command=self.menuReplace)
        helpmenu.add_command(label='{:16}'.format('Usage'),     accelerator='Ctrl+H',       command=self.menuUsage)
        menubar.add_cascade(label='File', menu=filemenu)
        menubar.add_cascade(label='Edit', menu=editmenu)
        menubar.add_cascade(label='Help', menu=helpmenu)
        

        mainTopFrame.pack   (side=tk.TOP,    fill=tk.BOTH, expand=tk.YES, padx=5, pady=5)
        mainBotFrame.pack   (side=tk.BOTTOM, fill=tk.X)
        mainTreTopFrame.pack(side=tk.TOP,    fill=tk.BOTH, expand=tk.YES)
        mainEtyTopFrame.pack(side=tk.TOP,    fill=tk.X)
        mainLblBotFrame.pack(side=tk.LEFT,   fill=tk.X,    expand=tk.YES, padx=5)
        mainPrgBotFrame.pack(side=tk.RIGHT,  fill=tk.X)
        treeTop.pack        (side=tk.LEFT,   fill=tk.BOTH, expand=tk.YES)
        scrlTop.pack        (side=tk.RIGHT,  fill=tk.Y)
        etryTop.pack        (side=tk.LEFT,   fill=tk.X,    expand=tk.YES)
        lbelBot.pack        (side=tk.LEFT,   fill=tk.X,    expand=tk.YES)
        prgsBot.pack        (side=tk.RIGHT,  fill=tk.X,    expand=tk.YES)
        window.config       (menu=menubar)

        self.window  = window
        self.treeTop = treeTop
        self.scrlTop = scrlTop
        self.etryTop = etryTop
        self.lbelBot = lbelBot
        self.prgsBot = prgsBot
        self.archive = None

    def __fillTree(self):
        if not self.archive:
            return

        sectorsize = self.archive.getSectorsize()
        for dentry in self.archive.getDentries():
                self.treeTop.insert(
                    '', tk.END, 
                    text=dentry['snme'], 
                    values=(
                        '0x{:06x}'.format(dentry['ofst']),
                        '{} KB'   .format((dentry['strm'] * sectorsize) // 1024)
                    )
                )


    def __filtTree(self, match):
        for child in self.treeTop.get_children():
            item = self.treeTop.item(child)
            if match not in item['text']:
                self.treeTop.delete(child)


    def __eptyTree(self):
        for child in self.treeTop.get_children():
            self.treeTop.delete(child)

    def run(self):
        self.window.mainloop()
        
    def searchDentry(self, event):
        match = self.etryTop.get()
        self.__eptyTree()
        self.__fillTree()
        if match:
            self.__filtTree(match)

    def prgsBarCallback(self, value, maximum):
        self.prgsBot['maximum'] = maximum
        self.prgsBot['value']   = value  
        self.prgsBot.update() 

    def menuOpen(self):
        if self.archive:
            return

        filename = tk.filedialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=(('img files','*.img'),('all files','*.*'))
        )
        if not filename:
            return

        self.archive = img.IMGArchive(filename, self.prgsBarCallback)
        self.__fillTree()
        self.log('Archive loaded. ({} files)'.format(self.archive.getNentries()))
    
    def menuSave(self):
        if not self.archive:
            return
        
        filename = self.archive.filestream.name
        self.archive.save(filename, self.prgsBarCallback)
        self.log('Archive saved. ({})'.format(os.path.basename(filename)))


    def menuSaveAs(self):
        if not self.archive:
            return
        
        filename = tk.filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            defaultextension='.img',
            filetypes=(('img files','*.img'),('all files','*.*'))
        )
        if not filename:
            return

        self.archive.save(filename, self.prgsBarCallback)
        self.log('Archive saved. ({})'.format(os.path.basename(filename)))

    def menuClose(self):
        if not self.archive:
            return

        del self.archive
        self.archive = None
        self.__eptyTree()
        self.log('{} ready.'.format(self.title))

    def menuExtract(self):
        if not self.archive:
            return
        
        for item in self.getSelectedItems():
            filename = tk.filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                initialfile=item['snme']
            )
            if not filename:
                continue

            self.archive.extract(item['snme'], filename)
            self.log('File extracted. ({})'.format(os.path.basename(filename)))

    def menuReplace(self):
        if not self.archive:
            return

        items = self.getSelectedItems()
        if items == []:
            return

        filename = tk.filedialog.askopenfilename(
            initialdir=os.getcwd()
        )
        if not filename:
            return

        for item in items:
            self.archive.replace(item['snme'], filename)
            self.log('File replaced. ({})'.format(item['snme']))


    def menuUsage(self):
        webbrowser.open_new(self.usageUrl)

    def log(self, message):
        self.lbelBot.configure(text=message)


    def shutdown(self):
        self.menuClose()
        self.window.quit()


    def getSelectedItems(self):
        items = []
        for item in self.treeTop.selection():
            item = self.treeTop.item(item)
            items.append(
                {
                    'snme': item['text'],
                    'ofst': item['values'][0],
                    'size': item['values'][1]
                }
            )
        
        return items


    def shortcutHandle(self, key):
        keybinds = {
            (4,'s') : self.menuSave,    #save
            (5,'S') : self.menuSaveAs,  #save as
            (4,'o') : self.menuOpen,    #open
            (4,'q') : self.menuClose,   #close
            (4,'e') : self.menuExtract, #extract
            (4,'r') : self.menuReplace, #replace
            (4,'h') : self.menuUsage,   #usage
        }
        
        keybinds.get((key.state,key.keysym), lambda *args: None)()

    

if __name__ == '__main__':
    app = Application()
    app.run()
