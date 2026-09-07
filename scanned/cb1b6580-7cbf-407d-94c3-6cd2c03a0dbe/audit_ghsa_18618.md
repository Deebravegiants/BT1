# [H] pyLoad CNL and captcha handlers allow Code Injection via unsanitized parameters

## Summary
Severity: High
Advisory: GHSA-cjjf-27cc-pvmv
CVE: CVE-2025-61773
CWE: CWE-116, CWE-74, CWE-79, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-cjjf-27cc-pvmv
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev91

## Details
### Summary
pyLoad web interface contained insufficient input validation in both the Captcha script endpoint and the Click'N'Load (CNL) Blueprint. This flaw allowed untrusted user input to be processed unsafely, which could be exploited by an attacker to inject arbitrary content into the web UI or manipulate request handling. The vulnerability could lead to client-side code execution (XSS) or other unintended behaviors when a malicious payload is submitted.

user-supplied parameters from HTTP requests were not adequately validated or sanitized before being passed into the application logic and response generation. This allowed crafted input to alter the expected execution flow.
 CNL (Click'N'Load) blueprint exposed unsafe handling of untrusted parameters in HTTP requests. The application did not consistently enforce input validation or encoding, making it possible for an attacker to craft malicious requests.

### PoC

1. Run a vulnerable version of pyLoad prior to commit [`f9d27f2`](https://github.com/pyload/pyload/pull/4624).
2. Start the web UI and access the Captcha or CNL endpoints.
3. Submit a crafted request containing malicious JavaScript payloads in unvalidated parameters (`/flash/addcrypted2?jk=function(){alert(1)}&crypted=12345`).
4. Observe that the payload is reflected and executed in the client’s browser, demonstrating cross-site scripting (XSS).

Example request:

```http
GET /flash/addcrypted2?jk=function(){alert(1)}&crypted=12345 HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/x-www-form-urlencoded
Content-Length: 107
```

### Refferences
- https://github.com/pyload/pyload/commit/5823327d0b797161c7195a1f660266d30a69f0ca
- [`@4624`](https://github.com/pyload/pyload/pull/4624)

### Impact

Exploiting this vulnerability allows an attacker to inject and execute arbitrary JavaScript within the browser session of a user accessing the pyLoad Web UI. In practice, this means an attacker could impersonate an administrator, steal authentication cookies or tokens, and perform unauthorized actions on behalf of the victim. Because the affected endpoints are part of the core interface, a successful attack undermines the trust and security of the entire application, potentially leading to a full compromise of the management interface and the data it controls. The impact is particularly severe in cases where the Web UI is exposed over a network without additional access restrictions, as it enables remote attackers to directly target users with crafted links or requests that trigger the vulnerability.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-cjjf-27cc-pvmv
- https://nvd.nist.gov/vuln/detail/CVE-2025-61773
- https://github.com/pyload/pyload/pull/4624
- https://github.com/pyload/pyload/commit/5823327d0b797161c7195a1f660266d30a69f0ca
- https://github.com/pyload/pyload
