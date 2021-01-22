# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Optional

import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType, SessionStarted, ActionExecuted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

class ActionSlotReset(Action):

    def name(self) -> Text:
        return "action_slot_reset"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]


class ActionQuerySlots(Action):
    def name(self) -> Text:
        return "action_slot_query"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try: 
            r = requests.get('https://1ntj0abfh0.execute-api.us-east-1.amazonaws.com/PROD/customer?contactId='+ tracker.sender_id)
        
            name = r.json()[0]["fname"]
            sex = r.json()[0]["sex"]
            events = [SlotSet("name", name), SlotSet("sex", sex)]
            return events
        except: 
            return [SlotSet("name", "DemoMan"), SlotSet("sex", "man")]
        
class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"


    async def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # the session should begin with a `session_started` event
        events = [SessionStarted()]
        try: 
            r = requests.get('https://1ntj0abfh0.execute-api.us-east-1.amazonaws.com/PROD/customer?contactId='+ tracker.sender_id)
            print(r.status_code)
            if r.status_code > 300:
                
                raise  Exception("No Data supplied")
            data = r.json()
            for key in data:
                events.append(SlotSet(key, data[key]))
        except: 
            data = {
                "name": "DemoMan",
                "payment_amount": "500 pesos",
                "payment_date": "22 de Enero"
            }

            for key in data:
                events.append(SlotSet(key, data[key]))

        # an `action_listen` should be added at the end as a user message follows
        events.append(ActionExecuted("action_listen"))
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

class ValidatePaymentForm(Action):
    def name(self) -> Text:
        return "payment_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["accept_payment"]
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ValidateRejPaymentForm(Action):
    def name(self) -> Text:
        return "reject_payment_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["accept_payment", "reason_rejection"]
        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class PaymentMessage(Action):
    def name(self) -> Text:
        return "action_utter_message"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("accept_payment") == False:
            dispatcher.utter_message(template="utter_payment_reject")
        if tracker.get_slot("accept_payment") == True:
            dispatcher.utter_message(template="utter_payment_accept")
        return []

class NewPolicyMessage(Action):
    def name(self) -> Text:
        return "action_new_policy_message"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("accept_new_policy") == False:
            dispatcher.utter_message(template="utter_goodbye")
        if tracker.get_slot("accept_new_policy") == True:
            dispatcher.utter_message(template="utter_handover")
        return []