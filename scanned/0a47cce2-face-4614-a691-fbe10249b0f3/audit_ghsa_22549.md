# [M] Mautic Cross Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-358v-cqjc-2pcq
CVE: CVE-2017-1000506
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-358v-cqjc-2pcq
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <2.14.2

## Details
Mautic version 2.11.0 and earlier contains a Cross Site Scripting (XSS) vulnerability in Company's name that can result in denial of service and execution of javascript code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000506
- https://github.com/mautic/mautic/issues/5222
- https://github.com/mautic/mautic
