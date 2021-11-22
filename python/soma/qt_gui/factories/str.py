# -*- coding: utf-8 -*-

from pydantic import ValidationError

from soma.qt_gui.qt_backend import Qt
from soma.qt_gui.factories import WidgetFactory
from soma.qt_gui.timered_widgets import TimeredQLineEdit
from soma.undefined import undefined

class StrWidgetFactory(WidgetFactory):
    def create_widgets(self):
        label = self.parent_interaction.get_label()
        self.label_widget = Qt.QLabel(label, parent=self.controller_widget)
        self.text_widget = TimeredQLineEdit(parent=self.controller_widget)

        self.parent_interaction.on_change_add(self.update_gui)
        self.update_gui()

        self.text_widget.userModification.connect(self.update_controller)

        self.controller_widget.add_widget_row(self.label_widget, self.text_widget)

    def delete_widgets(self):
        self.controller_widget.remove_widget_row()
        self.text_widget.userModification.disconnect(self.update_controller)
        self.parent_interaction.on_change_remove(self.update_gui)
        self.label_widget.deleteLater()
        self.text_widget.deleteLater()

    def update_gui(self):
        value = self.parent_interaction.get_value()
        if value is undefined:
            self.text_widget.setText('')
            if self.parent_interaction.is_optional():
                self.text_widget.setStyleSheet(self.warning_style_sheet)
            else:
                self.text_widget.setStyleSheet(self.invalid_style_sheet)
        else:
            self.text_widget.setStyleSheet(self.valid_style_sheet)
            self.text_widget.setText(f'{value}')

    def update_controller(self):
        try:
            self.parent_interaction.set_value(self.text_widget.text())
        except ValidationError:
            self.text_widget.setStyleSheet(self.invalid_style_sheet)
        else:
            self.parent_interaction.set_protected(False)
            self.text_widget.setStyleSheet(self.valid_style_sheet)
