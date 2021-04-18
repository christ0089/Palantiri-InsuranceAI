# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Optional

import requests
import logging
logger = logging.Logger(__name__)

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
                "payment_date": "22 de Enero",
                "insurance_type": "Casa"
            }

            for key in data:
                events.append(SlotSet(key, data[key]))

        # an `action_listen` should be added at the end as a user message follows
        events.append(ActionExecuted("action_listen"))
        return events

class ValidatePolicyForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_policy_sale"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Optional[List[Text]]:
        additional_slots = []
        print(slots_mapped_in_domain)
        print(tracker.slots.get("A_has_insurance"))
        print(tracker.slots.get("B_interested"))
        if tracker.slots.get("A_has_insurance") is False:
            additional_slots .append("D_reasoning_for_rejection")
            return slots_mapped_in_domain + additional_slots
        if tracker.slots.get("B_interested") is False:
            # If the user wants to sit outside, ask
            # if they want to sit in the shade or in the sun.
            additional_slots .append("B_interested")
            additional_slots .append("D_reasoning_for_rejection")
            return slots_mapped_in_domain + additional_slots
        elif tracker.slots.get("B_interested") == True:
            additional_slots.append("B_interested")
            ##additional_slots.append("C_city")
            print(slots_mapped_in_domain + additional_slots)
            return slots_mapped_in_domain + additional_slots
        elif tracker.slots.get("A_has_insurance") == True:
            additional_slots.append("B_interested")
            print(slots_mapped_in_domain + additional_slots)
            return slots_mapped_in_domain + additional_slots


        return slots_mapped_in_domain + additional_slots
    
    async def extract_B_interested(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        intent = tracker.latest_message.get("intent")
        print(intent["name"])

        last_event = tracker.events[-1]
        print(last_event)

        if last_event["event"] == "slot" and last_event["name"] == "A_has_insurance" :
            return  {"B_interested": None}
        interest =  False if intent["name"] == "deny" else True
        return {"B_interested": interest}
    
    async def extract_C_city(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        entities = tracker.latest_message.get("entities")
        print(entities)
        last_event = tracker.events[-1]
        if last_event["event"] == "slot" and last_event["name"] == "B_interested" :
            return  {"C_city": None}

        for dictionary in entities:
            if dictionary["entity"] == "city":
                return {"C_City": dictionary["value"]}
                
        return {"C_city": None}

    async def extract_D_reasoning_for_rejection(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        text = tracker.latest_message.get("text")
        intent = tracker.latest_message.get("intent")

   
        last_event = tracker.events[-1]

        print(text)
        if last_event["event"] == "slot" and last_event["name"] == "B_interested" :
            return  {"D_reasoning_for_rejection": None}
        if last_event["event"] == "slot" and last_event["name"] == "A_has_insurance" :
            return  {"D_reasoning_for_rejection": None}
        if intent["name"] == "deny":
            return {"D_reasoning_for_rejection": text}
                
        return {"D_reasoning_for_rejection": text}


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