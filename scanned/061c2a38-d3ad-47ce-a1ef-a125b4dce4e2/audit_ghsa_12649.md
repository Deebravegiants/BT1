# [M] NodCMS Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7xqx-xwg9-jx34
CVE: CVE-2020-20697
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-7xqx-xwg9-jx34
Type: github-advisory

## Affected
- Packagist: `khodakhah/nodcms` — affected >=0

## Details
Cross Site Scripting vulnerability in khodakhah NodCMS v.3.0 allows an attacker with administrative privileges to execute arbitrary code and gain access to sensitive information via a crafted script to the address parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-20697
- https://github.com/khodakhah/nodcms/issues/41
- https://github.com/khodakhah/nodcms
