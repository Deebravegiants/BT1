# [M] BlackSheep's ClientSession is vulnerable to CRLF injection

## Summary
Severity: Medium
Advisory: GHSA-6pw3-h7xf-x4gp
CVE: CVE-2026-22779
CWE: CWE-113, CWE-93
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-01-14
Source: https://github.com/advisories/GHSA-6pw3-h7xf-x4gp
Type: github-advisory

## Affected
- PyPI: `blacksheep` — affected >=0 <2.4.6

## Details
### Impact
The HTTP Client implementation in BlackSheep is vulnerable to CRLF injection. Missing headers validation makes it possible for an attacker to modify the HTTP requests (e.g. insert a new header) or even create a new HTTP request.
Exploitation requires developers to pass unsanitized user input directly into headers.
The server part is not affected because BlackSheep delegates to an underlying ASGI server handling of response headers.

**Attack vector:** Applications using user input in HTTP client requests (method, URL, headers).

### Patches
Users who use the HTTP Client in BlackSheep should upgrade to `2.4.6`.

### Workarounds
If users handle headers from untrusted parties, they might reject values for header names and values that contain carriage returns.

### References
https://owasp.org/www-community/vulnerabilities/CRLF_Injection

## References
- https://github.com/Neoteroi/BlackSheep/security/advisories/GHSA-6pw3-h7xf-x4gp
- https://nvd.nist.gov/vuln/detail/CVE-2026-22779
- https://github.com/Neoteroi/BlackSheep/commit/bd4ecb9542b5d52442276b5a6907931b90f38d12
- https://github.com/Neoteroi/BlackSheep
- https://github.com/Neoteroi/BlackSheep/releases/tag/v2.4.6
