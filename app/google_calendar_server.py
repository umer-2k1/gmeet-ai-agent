from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import TypedDict, List, Optional
import os
import dateparser


SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"

mcp = FastMCP("GoogleCalendar")


def get_service():
    creds = None
    print("------------ get_service ------------")
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


class EventInput(TypedDict):
    summary: str
    description: Optional[str]
    start: str
    end: str


class EventOutput(TypedDict):
    id: str
    summary: str
    description: str
    start: str
    end: str


#  ---- Tools ----
@mcp.tool()
async def create_event(input: EventInput) -> EventOutput:
    """
    Create a Google Calendar event.

    Args:
        input (EventInput): Contains summary, description (optional), start (ISO 8601), and end (ISO 8601).

    Returns:
        EventOutput: Created event data with id, summary, description, start, and end.
    """
    print("create_event", input)
    service = get_service()
    print("service----------------------", service)
    start_dt = dateparser.parse(input["start"])
    end_dt = dateparser.parse(input["end"])
    event = {
        "summary": input["summary"],
        "description": input.get(
            "description", "Event created from the LangChain toolkit"
        ),
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "UTC",
        },
    }
    event = await service.events().insert(calendarId="primary", body=event).execute()
    return {
        "id": event["id"],
        "summary": event["summary"],
        "description": event["description"],
        "start": event["start"]["dateTime"],
        "end": event["end"]["dateTime"],
    }


@mcp.tool()
async def get_events(start: str, end: str) -> List[EventOutput]:
    """Get all events in the user's calendar between the given dates."""
    service = await get_service()
    events_result = (
        service.events()
        .list(calendarId="primary", timeMin=start, timeMax=end)
        .execute()
    )
    events = events_result.get("items", [])
    return [event_to_output(event) for event in events]


@mcp.tool()
async def delete_event(id: str) -> None:
    """Delete the event with the given ID."""
    service = get_service()
    await service.events().delete(calendarId="primary", eventId=id).execute()
    return {"status": "deleted", "id": id}


def event_to_output(event):
    return {
        "id": event["id"],
        "summary": event["summary"],
        "description": event["description"],
        "start": event["start"]["dateTime"],
        "end": event["end"]["dateTime"],
    }


if __name__ == "__main__":
    # service = get_service()
    # print("MY SERVICE", service.events().list(calendarId="primary").execute())
    mcp.run(transport="stdio")
