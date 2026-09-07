# [H] Cross-site Scripting (XSS) in CrafterCMS

## Summary
Severity: High
Advisory: GHSA-jfm4-3vv3-fm4v
CVE: CVE-2023-4136
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-03
Source: https://github.com/advisories/GHSA-jfm4-3vv3-fm4v
Type: github-advisory

## Affected
- Maven: `org.craftercms:crafter-engine` — affected >=4.0.0 <4.0.3
- Maven: `org.craftercms:crafter-engine` — affected >=3.1.0 <3.1.28

## Details
Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in CrafterCMS Engine on Windows, MacOS, Linux, x86, ARM, 64 bit allows Reflected XSS.This issue affects CrafterCMS: from 4.0.0 through 4.0.2, from 3.1.0 through 3.1.27.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4136
- https://docs.craftercms.org/en/4.0/security/advisory.html#cv-2023080301
- https://github.com/craftercms/engine
- http://packetstormsecurity.com/files/174304/CrafterCMS-4.0.2-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2023/Aug/30
