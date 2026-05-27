import sqlite3
try:
    import tkinter
except ImportError:  # python 2
    import Tkinter as tkinter

conn = sqlite3.connect('brian_cds.sqlite')


class Scrollbox(tkinter.Listbox):

    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)
        self.scrollbar = tkinter.Scrollbar(window, orient='vertical', command=self.yview)

    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set


def get_albums(event):
    lb = event.widget
    if not lb.curselection():
        return
    index = lb.curselection()[0]
    artist_display_name = lb.get(index)
    aid = artist_name_to_id_map[artist_display_name]
    try:
        aid_int = int(aid)
        albums_list = [album[0] for album in conn.execute(
            "SELECT cd.title FROM cd WHERE cd.artist_id = ? ORDER BY cd.orig_album_release_date",
            (aid_int,))]
        albumLV.set(tuple(albums_list))
        albumList.selection_clear(0, tkinter.END)
        albumList.yview_moveto(0)
    except (ValueError, TypeError):
        albumLV.set(("Error loading albums",))



mainWindow = tkinter.Tk()
mainWindow.title('Music DB Browser')
mainWindow.geometry('1024x768')

mainWindow.columnconfigure(0, weight=2)
mainWindow.columnconfigure(1, weight=2)
mainWindow.columnconfigure(2, weight=2)
mainWindow.columnconfigure(3, weight=1)  # spacer column on right

mainWindow.rowconfigure(0, weight=1)
mainWindow.rowconfigure(1, weight=5)
mainWindow.rowconfigure(2, weight=5)
mainWindow.rowconfigure(3, weight=1)

# ===== labels =====
tkinter.Label(mainWindow, text="Artists").grid(row=0, column=0)
tkinter.Label(mainWindow, text="Albums").grid(row=0, column=1)
tkinter.Label(mainWindow, text="Songs").grid(row=0, column=2)

# ===== Artists Listbox =====
artistList = Scrollbox(mainWindow, exportselection=False)
artistList.grid(row=1, column=0, sticky='nsew', rowspan=2, padx=(30, 0))
artistList.config(border=2, relief='sunken')

artist_name_to_id_map = {}

for artist in conn.execute("SELECT artist.artist_id, artist.artist_display_name FROM artist ORDER BY artist.artist_sort_name COLLATE NOCASE"):
    artist_id, artist_display_name = artist
    artistList.insert(tkinter.END, artist_display_name)
    artist_name_to_id_map[artist_display_name] = artist_id

artistList.bind('<<ListboxSelect>>', get_albums)

# ===== Albums Listbox =====
albumLV = tkinter.Variable(mainWindow)
albumLV.set(("Choose an artist",))
albumList = Scrollbox(mainWindow, listvariable=albumLV)
albumList.grid(row=1, column=1, sticky='nsew', padx=(30, 0))
albumList.config(border=2, relief='sunken')



# ===== Songs Listbox =====
songLV = tkinter.Variable(mainWindow)
songLV.set(("Choose an album",))
songList = Scrollbox(mainWindow, listvariable=songLV)
songList.grid(row=1, column=2, sticky='nsew', padx=(30, 0))
songList.config(border=2, relief='sunken')

# ===== Main loop
mainWindow.mainloop()
print("Closing database connection")
conn.close()


