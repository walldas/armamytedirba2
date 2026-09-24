import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.pythonanywhere.com"


def renew_pythonanywhere():
    username = os.environ["PA_USERNAME"].strip()
    password = os.environ["PA_PASSWORD"].strip()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    login_url = f"{BASE_URL}/login/"
    login_page = session.get(login_url, timeout=20)
    login_page.raise_for_status()

    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf = soup.find("input", {"name": "csrfmiddlewaretoken"})
    if not csrf:
        raise RuntimeError("PythonAnywhere login CSRF token not found")

    response = session.post(
        login_url,
        data={
            "csrfmiddlewaretoken": csrf["value"],
            "auth-username": username,
            "auth-password": password,
            "login_view-current_step": "auth",
        },
        headers={"Referer": login_url},
        timeout=20,
        allow_redirects=True,
    )
    response.raise_for_status()

    if "log out" not in response.text.lower() or "login" in response.url.lower():
        raise RuntimeError("PythonAnywhere login failed")

    dashboard_url = f"{BASE_URL}/user/{username}/webapps/"
    dashboard = session.get(dashboard_url, timeout=20)
    dashboard.raise_for_status()
    soup = BeautifulSoup(dashboard.text, "html.parser")

    forms = [
        form
        for form in soup.find_all("form", action=True)
        if "/extend" in form["action"].lower()
    ]

    if not forms:
        print("No web-app renewal form found. Nothing to renew.")
        return

    renewed = 0

    for form in forms:
        csrf = form.find("input", {"name": "csrfmiddlewaretoken"})
        if not csrf:
            raise RuntimeError("Renewal form CSRF token not found")

        action = urljoin(BASE_URL, form["action"])
        result = session.post(
            action,
            data={"csrfmiddlewaretoken": csrf["value"]},
            headers={"Referer": dashboard_url},
            timeout=20,
            allow_redirects=True,
        )
        result.raise_for_status()

        if "webapps" not in result.url.lower():
            raise RuntimeError(f"Unexpected renewal response: {result.url}")

        renewed += 1
        print(f"Renewed: {action}")

    print(f"PythonAnywhere renewal completed. Web apps renewed: {renewed}")


if __name__ == "__main__":
    renew_pythonanywhere()
