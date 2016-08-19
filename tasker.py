# https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller
# TODO: Configure theme properly (window margins, padding, etc.)
# TODO: Add editability for the tasks. Enter 'edit mode' from 'normal mode'***
# TODO: Add undo feature to undo most recent change
# TODO: Add creation of new tasks***
# TODO: Parse input arguments (fullscreen, opacity, stylesheet, etc.)
# TODO: Scrollbar for long lists of tasks

import sys, gi
import simplejson as json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

# from datetime import datetime as dt
# dt.strptime(s, '%Y-%m-%dT%H:%M:%S.%f') # datetime isoformat


class EntryBox(Gtk.Window):

    # grid = Gtk.Grid()
    #
    # # Construct first row
    # name_label = Gtk.Label('Name')
    # self.name_entry = Gtk.Entry()
    # grid.attach(name_label, 0, 0, 2, 2)
    # grid.attach(self.name_entry, 2, 0, 3, 2)
    #
    # # Construct second row
    # descript_label = Gtk.Label('Description')
    # self.descript_entry = Gtk.Entry()
    # grid.attach(descript_label, 0, 2, 2, 2)
    # grid.attach(self.descript_entry, 2, 2, 3, 2)

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_default_size(width=300, height=150)
        self.connect('key-press-event', self.on_key_function)

        box = Gtk.ListBox()

        # Construct first row
        name_row = Gtk.ListBoxRow()
        name_hbox = Gtk.HBox()
        name_hbox.add(Gtk.Label('Name'))
        self.name_entry = Gtk.Entry()
        self.name_entry.set_width_chars(80)
        name_hbox.add(self.name_entry)
        name_row.add(name_hbox)

        # Construct second row
        descript_row = Gtk.ListBoxRow()
        descript_hbox = Gtk.HBox()
        descript_hbox.add(Gtk.Label('Description'))
        self.descript_entry = Gtk.Entry()
        self.descript_entry.set_width_chars(80)
        descript_hbox.add(self.descript_entry)
        descript_row.add(descript_hbox)

        box.add(name_row)
        box.add(descript_row)
        self.add(box)
        self.show_all()

    def on_key_function(self, widget, event):

        if event.keyval == Gdk.KEY_Escape:
            self.close()
        elif event.keyval == Gdk.KEY_Return:
            if len(self.descript_entry.get_text()) != 0 and len(self.name_entry.get_text()) != 0:
                self.close()


class Controller(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, title="TODO")
        self.set_default_size(width=400, height=200)
        self.set_accept_focus(True)
        # self.set_decorated(False)
        # self.fullscreen()
        self.css_config('style.css')

        self.connect("destroy", lambda x: Gtk.main_quit())
        self.connect('key-press-event', self.on_key_function)

        self.model = Model("tasks.json")
        self.view = View(self.model)

        self.add(self.view)
        self.show_all()
        self.set_opacity(0.7)

        Gtk.main()

    def on_key_function(self, widget, event):

        # Quit the application
        if event.keyval == Gdk.KEY_Escape:
            # self.model.save_data()
            Gtk.main_quit()

        # Remove a row from the model
        elif event.keyval == Gdk.KEY_Delete:
            try:
                path = self.get_selected_row()
            except IndexError:
                return

            self.model.remove(self.model.get_iter(path))

        # Toggle the task
        elif event.keyval == Gdk.KEY_space:
            try:
                path = self.get_selected_row()
            except IndexError:
                return

            self.model[path][Model.labels['complete']] = not self.model[path][Model.labels['complete']]
            self.model.sort_model()
            self.view.set_cursor(path)

        # elif event.keyval == Gdk.KEY_e:
        #     self.editing = True
        #
        # # Create a new entry at the top of the list
        # elif event.keyval == Gdk.KEY_n:
        #     self.model.prepend(["004", "", "", False, ""])
        #     self.view.set_cursor(0)

        elif event.keyval == Gdk.KEY_n:
            self.create_new_entry_box()

    def get_selected_row(self):
        selection = self.view.get_selection()
        path = selection.get_selected_rows()[1].__getitem__(0)
        return path

    def create_new_entry_box(self):
        e = EntryBox()
        print e.name_entry, e.descript_entry

    def css_config(self, css_file):
        provider = Gtk.CssProvider()
        with open(css_file, 'r') as f:
            provider.load_from_data(f.read())
        screen = Gdk.Screen.get_default()
        context = self.get_style_context()
        context.add_provider_for_screen(
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

class Model(Gtk.ListStore):

    labels = {
        "id":0,
        "name":1,
        "description":2,
        "complete":3,
        "time":4
    }

    def __init__(self, filename):

        Gtk.ListStore.__init__(self, str, str, str, bool, str)
        
        self.filename = filename
        data = self.load_data()
        for i in data:
            self.append([i] + data[i])

        self.sort_model()

    def sort_model(self):
        d = [[i] + list(row) for (i, row) in enumerate(self)]
        new_order = [i[0] for i in sorted(d, key=lambda s: s[Model.labels['complete']+1])]
        self.reorder(new_order)

    def load_data(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

    def save_data(self):
        with open(self.filename, 'w') as f:
            data = {}
            for row in self:
                data[row[0]] = row[1:]
            json.dump(data, f)


class View(Gtk.TreeView):

    def __init__(self, model):
        Gtk.TreeView.__init__(self, model)

        self.set_enable_search(False)
        self.set_rules_hint(True)

        # Create the CellRenderers for each of the TreeViewColumns
        self.renderer0 = Gtk.CellRendererText()
        self.renderer0.set_property('editable', False)

        self.renderer1 = Gtk.CellRendererText()
        self.renderer1.set_property('editable', False)

        self.renderer2 = Gtk.CellRendererToggle()
        self.renderer2.set_property('activatable', True)

        # Create the TreeViewColumns for the TreeView
        self.column0 = Gtk.TreeViewColumn("Name", self.renderer0, text=Model.labels['name'], strikethrough=Model.labels['complete'])
        self.column1 = Gtk.TreeViewColumn("Description", self.renderer1, text=Model.labels['description'], strikethrough=Model.labels['complete'])
        self.column2 = Gtk.TreeViewColumn("Complete", self.renderer2, active=Model.labels['complete'])

        self.column0.set_fixed_width(300)
        self.column1.set_fixed_width(400)

        # Add columns to the view
        self.append_column(self.column0)
        self.append_column(self.column1)
        self.append_column(self.column2)

def main():
    Controller()

if __name__ == '__main__':
    main()

