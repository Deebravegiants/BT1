# [C] PyroCMS vulnerable to stored Cross Site Scripting

## Summary
Severity: Critical
Advisory: GHSA-cm7f-hf2g-ghrp
CVE: CVE-2022-37721
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-25
Source: https://github.com/advisories/GHSA-cm7f-hf2g-ghrp
Type: github-advisory

## Affected
- Packagist: `pyrocms/pyrocms` — affected >=0

## Details
PyroCMS 3.9 is vulnerable to a stored Cross Site Scripting (XSS) when a low privileged user, such as an author, injects a crafted html and javascript payload in a blog post, leading to full admin account takeover or privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37721
- https://github.com/pyrocms/pyrocms
- https://labs.integrity.pt/advisories/cve-2022-37721
