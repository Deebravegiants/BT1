# [M] Moderate severity vulnerability that affects io.undertow:undertow-core

## Summary
Severity: Medium
Advisory: GHSA-3x7h-5hfr-hvjm
CVE: CVE-2017-2670
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-3x7h-5hfr-hvjm
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <1.3.28

## Details
It was found in Undertow before 1.3.28 that with non-clean TCP close, the Websocket server gets into infinite loop on every IO thread, effectively causing DoS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2670
- https://github.com/advisories/GHSA-3x7h-5hfr-hvjm
