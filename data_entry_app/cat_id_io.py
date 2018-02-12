from pandas import DataFrame, read_pickle
from kivy.app import App
# from kivy.uix.behaviors import FocusBehavior
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
# from kivy.uix.image import Image
# from kivy.factory import Factory
# from kivy.resources import resource_add_path

import os

# def new_cat_attributes(dFrame, attrs):
#     """
#     Parameters
#     ----------
#     :param dFrame: pandas.core.frame.DataFrame
#         The data frame to append a new row of attributes to
#     :param attrs: dict
#
#
#     :return:
#     """
# The above is all unnecessary. Just use df = df.append({attribs_dict}, ignore_index=True)

# make a prototype GUI that can load an image. Make fields to enter data. Consider key strokes to enter data
# Lettings indiv. keystrokes enter data will speed up entry. Perhaps also allow drop-down?

cat_attribute_list = ['file_name', 'breed', 'primary_color', 'secondary_color', 'tertiary_color', 'color_modifier']


class LoadDialog(FloatLayout):
    # This should be a popup for loading images
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    last_path = StringProperty('')


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    new = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    last_path = StringProperty('')
    new_file = BooleanProperty(False)


class HintDialog(Popup):
    content = ObjectProperty(None)
    labels = ListProperty([])
    values = ListProperty([])


class FolderChangerDialog(Popup):
    folder_changer = ObjectProperty(None)
    text_input = ObjectProperty(None)
    example_path = StringProperty('')
    depth = ObjectProperty(None)
    depth_number = NumericProperty(0)
    cancel = ObjectProperty(None)
    last_path = StringProperty('')


class CatImage(FloatLayout):
    #loadfile = ObjectProperty(None)
    #savefile = ObjectProperty(None)
    last_path = StringProperty('')
    file_name = StringProperty('')
    remaining_images = ListProperty([])
    cat_image_list = ListProperty([])
    cat_image = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        # This must select the image to display
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup,
                             last_path=self.last_path)  # content = what shows up in the popup
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        self.cat_image.source = os.path.join(path, filename[0])
        self.cat_image.reload()
        self.last_path = path
        self.file_name = filename[0]
        all_files = os.listdir(path=path)
        self.remaining_images = [os.path.join(path, file) for file in all_files if file[-4:] == '.jpg']

        self.reconcile_cat_lists()

        self.dismiss_popup()

    def load_next(self, path, filename):
        try:
            self.cat_image.source = os.path.join(path, filename[0])
            self.file_name = filename[0]
        except IndexError:
            self.cat_image.source = ''

        self.cat_image.reload()
        self.last_path = path

    def reconcile_cat_lists(self):
        # This might come in handy after loading images and a dataframe
        for file in self.cat_image_list:
            try:
                self.remaining_images.remove(file)
            except ValueError:
                pass


class CatData(FloatLayout):
    last_path = StringProperty('')  # Path to the loaded dataframe, if it exists
    file_name = StringProperty('')  # Name of the loaded dataframe, if it exists
    cat_image_list = ListProperty([])  # list of cat images already ID'ed
    data_frame = ObjectProperty(None)
    reconciler = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        # This must select the image to display
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup,
                             last_path=self.last_path)  # content = what shows up in the popup
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        self.data_frame = read_pickle(filename[0])
        self.cat_image_list = self.data_frame['file_name'].tolist()
        self.reconciler()
        self.last_path = path
        self.file_name = filename[0]

        self.dismiss_popup()

    def show_save(self, new_file=False):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup,
                             last_path=self.last_path, new=self.new, new_file=new_file)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        try:
            self.data_frame.to_pickle(path=os.path.join(path, filename))
            self.file_name = os.path.join(path, filename)
        except AttributeError:
            return True

        self.dismiss_popup()
        return False  # This is so that I can grey out the save button if necessary

    def new(self):
        self.data_frame = DataFrame(columns=globals()['cat_attribute_list'].copy())

    def append(self, attribute_list):
        self.data_frame = self.data_frame.append(DataFrame(data=[attribute_list],
                                                              columns=globals()['cat_attribute_list']))

    def show_folder_changer(self):
        try:
            content = FolderChangerDialog(folder_changer=self.folder_changer, cancel=self.dismiss_popup,
                                         last_path=self.last_path, example_path=self.data_frame['file_name'].iloc[0])
            # content = what shows up in the popup.
            self._popup = Popup(title="Change data folder", content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
        except TypeError:
            # Clearly it would be better to tell users why nothing is happening, but this is fine.
            # I am only expecting one user right now.
            pass

    def folder_changer(self, new_folder, depth=0):
        # raise NotImplementedError  # I think I was replacing everything with the same name repeatedly.
        # define a function which changes the current folder hierarchy of the recorded data to a new one
        new_beginning = new_folder

        def _inside(series_obj):
            new_ending = '\\'.join(series_obj['file_name'].split('\\')[-(depth + 1):])
            return os.path.join(new_beginning, new_ending)

        self.data_frame['file_name'] = self.data_frame.apply(_inside, axis=1)
        self.dismiss_popup()


class CatAttribText(TextInput):
    valid_attributes = ListProperty([])

    def insert_text(self, substring, from_undo=False):
        try:
            s = self.valid_attributes[int(substring)-1]
            self.get_focus_next().focus = True
            return super(CatAttribText, self).insert_text(s, from_undo=from_undo)

        except IndexError:
            s = "Invalid selection. Try a (different) number."
            return super(CatAttribText, self).insert_text(s, from_undo=from_undo)

        except ValueError:
            # here we can add other character codes too, but this is a little...hacked together?
            if substring == 'q':
                _ = 9
            elif substring == 'w':
                _ = 10
            elif substring == 'e':
                _ = 11
            elif substring == 'a':
                _ = 12
            elif substring == 's':
                _ = 13
            elif substring == 'd':
                _ = 14
            else:
                _ = 10000
            try:
                s = self.valid_attributes[_]
                self.get_focus_next().focus = True
                return super(CatAttribText, self).insert_text(s, from_undo=from_undo)
            except IndexError:
                s = "Invalid selection. Try a (different) number."
                return super(CatAttribText, self).insert_text(s, from_undo=from_undo)


class CatIDScreen(Widget):
    cat_screen = ObjectProperty(None)
    cat_data = ObjectProperty(None)
    remaining_images = ListProperty([])
    cat_image_list = ListProperty([])
    cat_attribute_list = globals()['cat_attribute_list'].copy()
    to_append = ListProperty([])
    next_button = ObjectProperty(None)

    def reconcile_cat_lists(self):
        # This might come in handy after loading images and a dataframe
        for file in self.cat_image_list:
            try:
                self.remaining_images.remove(file)
            except ValueError:
                pass


class CatIDApp(App):
    # Write startup things here
    def build(self):
        screen = CatIDScreen()
        screen.last_path = os.curdir
        return screen


#Factory.register('CatIDScreen', cls=CatIDScreen)
#Factory.register('CatImage', cls=CatImage)
#Factory.register('LoadDialog', cls=LoadDialog)
#Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':

    CatIDApp().run()

