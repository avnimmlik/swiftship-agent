# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk import Context
from google.adk.workflow import Workflow, START
from google.genai import types

# Disable Vertex AI to use Developer API Key (Google AI Studio)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Define the models
# Note: we use "gemini-2.5-flash" as it is the standard model and supported
model = Gemini(
    model="gemini-3.6-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

async def classify_query(ctx: Context, node_input: str) -> str:
    """Classifies the user query as shipping-related or unrelated.

    Sets the workflow route to either 'shipping' or 'unrelated' based on the classification,
    and returns the original query.
    """
    from google import genai
    client = genai.Client()
    
    prompt = (
        "Classify if the following user query is related to shipping (rates, tracking, delivery, returns) or unrelated.\n"
        f"User query: '{node_input}'\n"
        "Output exactly 'shipping' if the query is related to shipping, or 'unrelated' if it is unrelated. "
        "Do not include any other text."
    )
    
    response = None
    for candidate_model in ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.8-flash']:
        try:
            response = await client.aio.models.generate_content(
                model=candidate_model,
                contents=prompt,
            )
            if response and response.text:
                break
        except Exception:
            continue
    
    classification = response.text.strip().lower() if response and response.text else "shipping"
    
    if "shipping" in classification:
        ctx.route = "shipping"
    else:
        ctx.route = "unrelated"

    # Return the original query so downstream nodes receive it as node_input
    return node_input


# Define the shipping FAQ agent
shipping_faq_agent = Agent(
    name="shipping_faq_agent",
    model=model,
    instruction=(
        "You are a fast, direct customer support agent for SwiftShip — a shipping and delivery company.\n\n"

        "## CRITICAL RULES\n"
        "- NEVER ask for a tracking number, order number, or any details UNLESS the user explicitly says they want to track a specific package.\n"
        "- Answer IMMEDIATELY using the knowledge below. Do NOT say 'please provide more details' for general questions.\n"
        "- Keep answers short, clear, and use bullet points where helpful.\n"
        "- If the user asks a general question (e.g. 'how long does delivery take?'), answer with the general policy — do NOT ask which order.\n\n"

        "## SHIPPING RATES\n"
        "- Standard (5–7 business days): ₹49 for up to 500g, ₹15 per additional 500g\n"
        "- Express (2–3 business days): ₹99 for up to 500g, ₹25 per additional 500g\n"
        "- Overnight (next business day, order before 6 PM): ₹199 flat for up to 2kg\n"
        "- International (7–14 business days): starts at ₹499, varies by country and weight\n"
        "- Free standard shipping on all orders above ₹999\n\n"

        "## DELIVERY TIMELINES\n"
        "- Standard: 5–7 business days after dispatch\n"
        "- Express: 2–3 business days after dispatch\n"
        "- Overnight: next business day if ordered before 6 PM\n"
        "- Remote areas may take 1–2 extra days\n"
        "- Orders are dispatched within 24 hours of placement on business days\n\n"

        "## TRACKING\n"
        "- Every order gets a tracking number via SMS and email after dispatch\n"
        "- Track at: swiftship.in/track or reply with your tracking number\n"
        "- Tracking updates within 2 hours of each scan\n"
        "- If tracking hasn't updated in 48 hours, escalate to support@swiftship.in\n\n"

        "## RETURNS & REFUNDS\n"
        "- Return window: 7 days from delivery\n"
        "- Items must be unused, in original packaging\n"
        "- Initiate a return at swiftship.in/returns or call 1800-XXX-XXXX\n"
        "- Refund processed within 5–7 business days after the return is received\n"
        "- Damaged/wrong item received? Full refund or re-shipment, no return needed — just send a photo\n\n"

        "## LOST OR DELAYED PACKAGES\n"
        "- If a package hasn't arrived after the expected window, it's considered delayed — not lost — until 3 business days past the expected date\n"
        "- After that, file a claim at swiftship.in/claim or email support@swiftship.in\n"
        "- Claims are resolved within 7 business days\n\n"

        "## PACKAGING & RESTRICTIONS\n"
        "- Max weight per parcel: 30kg\n"
        "- Max dimensions: 120cm x 80cm x 80cm\n"
        "- Prohibited: liquids, flammables, food items (unless sealed), live animals\n"
        "- Fragile items: double-pack and mark 'FRAGILE' — SwiftShip is not liable for improper packaging\n\n"

        "## CONTACT\n"
        "- Customer care: 1800-XXX-XXXX (Mon–Sat, 9 AM–7 PM)\n"
        "- Email: support@swiftship.in\n"
        "- Live chat: swiftship.in/chat\n"
    ),
)

# Define the decline node
def decline_query(node_input: str) -> str:
    """Politely declines to answer unrelated queries."""
    return (
        "I am sorry, but I can only assist with shipping-related queries (such as rates, tracking, delivery, or returns). "
        "Please let me know if you have a shipping-related question!"
    )

# Define the workflow
customer_support_workflow = Workflow(
    name="customer_support_workflow",
    edges=[
        (START, classify_query),
        (classify_query, {
            "shipping": shipping_faq_agent,
            "unrelated": decline_query,
        }),
    ],
)

# Instantiate the App
app = App(
    root_agent=customer_support_workflow,
    name="app",
)
