# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.executor import CollectingDispatcher

class ActionSlotReset(Action):

    def name(self) -> Text:
        return "action_slot_reset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]

class ActionCreateSlots(Action):
    def name(self) -> Text:
        return "action_slot_create"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot = tracker.get_slot('name')
        evt = [SlotSet("name", "Christian"), SlotSet("sex", "woman")]
        return evt

class ActionCreateSlots(Action):
    def name(self) -> Text:
        return "action_slot_query"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        r = requests.get('https://1ntj0abfh0.execute-api.us-east-1.amazonaws.com/PROD/customer?contactId=c3910e1e-3478-4c0a-ad28-5068a823f9b7')
        
        name = r.json()[0]["fname"]
        sex = r.json()[0]["sex"]
        events = [SlotSet("name", name), SlotSet("sex", sex)]
        return events

class ValidatePolicyForm(Action):
    def name(self) -> Text:
        return "policy_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["Acity", "Bdbo", "Dappointment"]
        if tracker.slots.get('sex') == "woman":
            required_slots = ["Acity", "Bdbo", "Cmaternity","Dappointment"]
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]


class actionHelloWorld(Action):

    def name(self) -> Text:
        return "action_get_dbo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        
        dispatcher.utter_message(text="Hello World!")

        return []
