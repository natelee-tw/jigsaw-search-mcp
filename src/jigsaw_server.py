import os
from typing import List
import requests
from dotenv import load_dotenv
import urllib3

from mcp.server.fastmcp import FastMCP

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = os.getenv("OKTA_OAUTH_URL")
auth = (os.getenv("NEO_USERNAME"), os.getenv("NEO_PASSWORD"))
headers = {"content-type": "application/x-www-form-urlencoded"}
data = {"grant_type": "client_credentials",
        "scope": "ApiCommonReadAccess"
}

response = requests.post(url, auth=auth, headers=headers, data=data, verify=False)
access_token = response.json().get("access_token")

# Initialize FastMCP server
mcp = FastMCP("jigsaw_server")
print("Starting Jigsaw server...")


@mcp.tool()
def search_role(role: str, working_office: str = "Singapore") -> List[str]:
    """
    Search for people on Jigsaw based on a role, grade, and working office.

    Role: The specific role to search for (e.g., "Developer", "Machine Learning Engineer", "Data Scientist", "Experience Designer", "Product Manager", "Business Analyst").
    Working Office: The office location to filter results (default is "Singapore").
    """

    url = os.getenv("JIGSAW_PEOPLE_URL")
    params = {
        "working_office": working_office,
        "role": f"{role}"
    }
    headers = {
        "authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers, params=params, verify=False)

    if response.status_code == 200:
        people = response.json()
        info = []
        for person in people:
            info.append({
                "employeeId": person.get("employeeId"),
                "preferredName": person.get("preferredName"),
                "gender": person.get("gender"),
                "role": person.get("role"),
                "grade": person.get("grade"),
                "hireDate": person.get("hireDate"),
                "totalExperience": person.get("totalExperience"),
                "twExperience": person.get("twExperience"),
                "homeOffice": person.get("homeOffice"),
                "workingOffice": person.get("workingOffice"),
            })
        return info

    else:
        print(f"Error fetching data from Jigsaw: {response.status_code}")
        return []


@mcp.prompt()
def generate_people_search_prompt(role: str, working_office: str = "Singapore") -> str:
    """
    Generate a natural language prompt to search for people based on role, grade, and working office.

    role: The specific role to search for (e.g., "Developer", "Machine Learning Engineer", "Data Scientist", "Experience Designer", "Product Manager", "Business Analyst").
    working_office: The office location to filter results (default is "Singapore") (e.g. New York, London, Singapore, ).

    Returns: A prompt string to search for matching people.
    """
    return (
        f"Find all people with the role '{role}', "
        f"and working in the '{working_office}' office."
    )


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
    
    # print(search_role("Machine Learning Engineer", "Singapore"))
