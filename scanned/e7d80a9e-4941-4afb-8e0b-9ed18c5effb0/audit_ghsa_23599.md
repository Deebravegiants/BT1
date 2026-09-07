# [M] Canvs Canvas XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-94hc-7qc9-34rf
CVE: CVE-2017-1000507
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-94hc-7qc9-34rf
Type: github-advisory

## Affected
- Packagist: `austintoddj/canvas` — affected >=0

## Details
Canvs Canvas version 3.4.2 contains a Cross Site Scripting (XSS) vulnerability in User's details that can result in denial of service and execution of javascript code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000507
- https://github.com/austintoddj/canvas/issues/359
- https://github.com/austintoddj/canvas
