# [M] Yamcs has DOM XSS in Extension Routing

## Summary
Severity: Medium
Advisory: GHSA-9272-wg2r-7xmx
CVE: CVE-2026-55566
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-9272-wg2r-7xmx
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs-core` — affected >=5.13.0 <5.13.2
- Maven: `org.yamcs:yamcs-core` — affected >=0 <5.12.8

## Details
**Attack type**: Unauthenticated remote 
**Impact**: Execution of arbitrary JavaScript in a user’s browser.
**Affected components**: extension.matcher.ts:12, extension.component.ts:40, app.component.ts:134.

Yamcs is vulnerable to cross-site scripting in the /ext URL endpoint. By inputting specially crafted code into the URL, an attacker can execute arbitrary JavaScript code in a user’s browser. This URL may be sent to a user via a phishing email.
 
<img width="940" height="294" alt="image" src="https://github.com/user-attachments/assets/d886d65c-9bb5-4599-ac11-55db83aafc0e" />

Steps to Reproduce:
1.	Start a Yamcs instance.
2.	Insert the following URL into the browser and press enter (change ‘myproject’ to the name of your instance):
```
http://localhost:8090/ext/img%20src%3Dx%20onerror%3Dalert%281%29?c=myproject
```
3.	You will receive an alert with the number ‘1’ in it.

Recommendations:
1.	Use document.createElement instead of innerHTML in extension.component.ts.
2.	Validate the extension against registered plugin IDs.
3.	Enforce a strict custom-element-name regex before mounting.

## References
- https://github.com/yamcs/yamcs/security/advisories/GHSA-9272-wg2r-7xmx
- https://github.com/yamcs/yamcs/commit/8e18e279d8ce761c21f4f67bbd06a1bff804d297
- https://github.com/yamcs/yamcs/commit/ecf34a4e2ccbe085e6ceff0253595b24d5ecb4aa
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.12.8
- https://github.com/yamcs/yamcs/releases/tag/yamcs-5.13.2
