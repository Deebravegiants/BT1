# [M] Undertow-core vulnerable to HTTP Request Smuggling

## Summary
Severity: Medium
Advisory: GHSA-mcfm-h73v-635m
CVE: CVE-2017-2666
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-mcfm-h73v-635m
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <1.3.31
- Maven: `io.undertow:undertow-core` — affected >=1.4.0 <1.4.17

## Details
It was discovered in Undertow that the code that parsed the HTTP request line permitted invalid characters. This could be exploited, in conjunction with a proxy that also permitted the invalid characters but with a different interpretation, to inject data into the HTTP response. By manipulating the HTTP response the attacker could poison a web-cache, perform an XSS attack, or obtain sensitive information from requests other than their own.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2666
- https://github.com/advisories/GHSA-mcfm-h73v-635m
