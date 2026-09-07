# [M] copyparty vulnerable to reflected cross-site scripting via hc parameter

## Summary
Severity: Medium
Advisory: GHSA-cw7j-v52w-fp5r
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-07-21
Source: https://github.com/advisories/GHSA-cw7j-v52w-fp5r
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.8.6

## Details
### Summary
The application contains a reflected cross-site scripting via URL-parameter `?hc=...`

### Details
A reflected cross-site scripting (XSS) vulnerability exists in the web interface of the application that could allow an attacker to execute malicious javascript code by tricking users into accessing a malicious link.

The worst-case outcome of this is being able to move or delete existing files on the server, or upload new files, using the account of the person who clicks the malicious link.

It is recommended to change the passwords of  your copyparty accounts, unless you have inspected your logs and found no trace of attacks.

### Checking for exposure
if copyparty is running behind a reverse proxy, you can check the access-logs for traces of attacks, by grepping for URLs containing `?hc=` with `<` somewhere in its value, for example using the following command:
* nginx:
  ```bash
  (gzip -dc access.log*.gz; cat access.log) | sed -r 's/" [0-9]+ .*//' | grep -E '[?&](hc|pw)=.*[<>]'
  ```


### PoC
* `http://127.0.0.1:3923/?hc="><script>alert(1);</script>`
* `http://127.0.0.1:3923/?pw=<script>alert(1);</script>`

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-cw7j-v52w-fp5r
- https://github.com/9001/copyparty/commit/0778da6c4d04de870c61f970763a7b619094093c
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.8.6
