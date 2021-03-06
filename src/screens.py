# -*- coding: utf-8 -*-
from functools import partial
from datetime import datetime

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout


from kivy.uix.label import Label
from kivy.uix.button import Button
from npt_events import Event, EVALUATION_POSITIVE, EVALUATION_NEGATIVE, FILTERS, ALL_FILTER


HISTORY_SCREEN_NAME = 'History Screen'
MAIN_SCREEN_NAME = 'Main Screen'


def rgb_to_kivy(*colors):
    alfa = colors[-1]
    rgb = [color / 255.0 for color in colors[:-1]]
    rgb.append(alfa)
    return rgb


class BasicScreen(Screen):
    def __init__(self, **kwargs):
        super(BasicScreen, self).__init__(**kwargs)
        self.events = []

    def load_events(self):
        return Event.get_events(self.manager.store)

    def on_pre_enter(self):
        self.events = self.load_events()
        self.update_screen_values()

    def update_screen_values(self):
        pass

    def add_new_event(self, evaluation):
        new_event = Event(date=datetime.now(), evaluation=evaluation)
        new_event.save(self.manager.store)
        self.events.append(
            new_event
        )


class MainScreen(BasicScreen):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.reset_count = 0
        self.add_widget(self._build_main_box())

    def _build_evaluation_box(self):
        evaluation_box = BoxLayout(orientation='horizontal')
        positive_button = Button(
            text="Positive",
            font_size=50,
            size_hint=(.5, .5),
            background_normal='',
            background_color=rgb_to_kivy(0, 102, 0, 1)
        )
        positive_button.bind(on_release=self.handle_positive_button)

        negative_button = Button(
            text="Negative",
            font_size=50,
            size_hint=(.5, .5),
            background_normal='',
            background_color=rgb_to_kivy(255, 0, 0, 1)
        )
        negative_button.bind(on_release=self.handle_negative_button)

        evaluation_box.add_widget(positive_button)
        evaluation_box.add_widget(negative_button)
        return evaluation_box

    def _build_botton_box(self):
        botton_box = BoxLayout(orientation='vertical', spacing=10)
        self.total_label = Label(font_size=30, color=[0, 0, 0, 1], size_hint=(1, 1))

        botton_box.add_widget(self.total_label)
        botton_box.add_widget(self._build_evaluation_box())
        return botton_box

    def _filter_layout(self):
        filter_box = BoxLayout(orientation='vertical', spacing=50)

        dropdown = DropDown()
        for filter_type in FILTERS.keys():
            filter_button = Button(
                text=filter_type,
                font_size=30,
                background_normal='',
                background_color=rgb_to_kivy(239, 93, 5, 1),
                size_hint_y=None,
                height=130
            )
            handle_filter_button_with_dropdown = partial(self.handle_filter_button, dropdown)
            filter_button.bind(on_release=handle_filter_button_with_dropdown)
            dropdown.add_widget(filter_button)

        filter_dropdown_btn = Button(
            text=ALL_FILTER,
            font_size=30,
            size_hint=(1, 1),
            background_normal='',
            background_color=rgb_to_kivy(239, 93, 5, 1)
        )
        filter_dropdown_btn.bind(on_release=dropdown.open)

        dropdown.bind(on_select=lambda instance, x: setattr(filter_dropdown_btn, 'text', x))
        filter_box.add_widget(filter_dropdown_btn)
        return filter_box

    def _menu_layout(self):
        menu_layout = RelativeLayout(
            size_hint=(None, None),
            size=(300, 100),
            pos_hint={'left': 1, 'top': 1},
        )
        menu_layout.add_widget(self._filter_layout())
        return menu_layout

    def _reset_layout(self):
        reset_layout = RelativeLayout(
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'right': 1, 'top': 1},
        )
        history_button = Button(
            text="History",
            font_size=30,
            size_hint=(1, 1),
        )
        history_button.bind(on_release=self.handle_history_button)
        reset_layout.add_widget(history_button)
        return reset_layout

    def _build_menu_and_reset(self):
        menu_and_reset_box = FloatLayout()

        menu_and_reset_box.add_widget(self._menu_layout())
        menu_and_reset_box.add_widget(self._reset_layout())
        return menu_and_reset_box

    def _build_top_box(self):
        top_box = BoxLayout(orientation='vertical')

        self.positive_label = Label(text="0%", font_size=150, color=rgb_to_kivy(239, 93, 5, 1), size_hint=(1, 1))

        top_box.add_widget(self._build_menu_and_reset())
        top_box.add_widget(self.positive_label)
        return top_box

    def _build_main_box(self):
        main_box = BoxLayout(orientation='vertical')
        main_box.add_widget(self._build_top_box())
        main_box.add_widget(self._build_botton_box())
        return main_box

    def update_positive_label(self):
        if not self.events:
            positive_perc = 100
        else:
            positive_perc = Event.get_rate(self.events)[0]
        self.positive_label.text = "{:.2f}%".format(positive_perc)

    def update_total_label(self):
        self.total_label.text = "Total Entries: {}".format(len(self.events))

    def update_screen_values(self):
        self.update_positive_label()
        self.update_total_label()

    def handle_positive_button(self, button):
        self.add_new_event(EVALUATION_POSITIVE)
        self.update_screen_values()

    def handle_negative_button(self, button):
        self.add_new_event(EVALUATION_NEGATIVE)
        self.update_screen_values()

    def handle_history_button(self, button):
        self.manager.current = HISTORY_SCREEN_NAME

    def handle_filter_button(self, dropdown, button):
        dropdown.select(button.text)
        filter_by = button.text
        filtered_events = Event.filter(self.manager.store, filter_by)
        self.events = filtered_events
        self.update_screen_values()


class HistoryScreen(BasicScreen):

    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.events = []
        self.add_widget(self._build_main_box())

    def load_events(self):
        events = Event.get_events(self.manager.store)
        events.sort(key=lambda x: x.date, reverse=True)
        return events[:7]

    def _build_main_box(self):
        main_box = BoxLayout(orientation='vertical')
        back_button = Button(
            text="Back",
            font_size=30,
            size_hint=(0.15, 0.15),
        )
        back_button.bind(on_release=self.handle_back_button)
        main_box.add_widget(back_button)
        main_box.add_widget(self._build_event_list())
        return main_box

    def _build_event_list(self):
        self.event_list_layout = BoxLayout(orientation='vertical', spacing=30)
        self.update_event_list()
        return self.event_list_layout

    def handle_back_button(self, button):
        self.manager.current = MAIN_SCREEN_NAME

    def _build_detail_event_box(self, event):
        event_layout = BoxLayout(orientation='horizontal')
        label_color = rgb_to_kivy(0, 102, 0, 1) if event.evaluation else rgb_to_kivy(255, 0, 0, 1)
        # event_eval_text = 'Positive' if event.evaluation else 'Negative'
        # event_text = "{} [{}]".format(event.date.strftime("%d/%m/%y  %H:%M:%S"), event_eval_text)
        event_text = event.date.strftime("%d/%m/%y  %H:%M:%S")
        event_label = Label(text=event_text, font_size=70, color=label_color, size_hint=(1, 1))

        event_rm_button = Button(
            text="-",
            font_size=50,
            size_hint=(.15, 1),
            background_normal='',
            background_color=rgb_to_kivy(255, 0, 0, 1)
        )
        handle_rm_with_event = partial(self.handle_rm_event, event)
        event_rm_button.bind(on_release=handle_rm_with_event)

        event_layout.add_widget(event_label)
        event_layout.add_widget(event_rm_button)
        return event_layout

    def update_event_list(self):
        self.event_list_layout.clear_widgets()
        for event in self.events:
            self.event_list_layout.add_widget(self._build_detail_event_box(event))

    def update_screen_values(self):
        self.events = self.load_events()
        self.update_event_list()

    def handle_rm_event(self, event, button):
        Event.remove_event(self.manager.store, event)
        self.update_screen_values()
