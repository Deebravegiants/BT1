# [M] Snipe-IT is vulnerable to stored cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-fww5-m9wc-jcjc
CVE: CVE-2025-65621
CWE: CWE-269, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-fww5-m9wc-jcjc
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.3.4

## Details
Snipe-IT before 8.3.4 allows stored XSS, allowing a low-privileged authenticated user to inject JavaScript that executes in an administrator's session, enabling privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65621
- https://github.com/firef0x00/vulnerability-research/tree/main/CVE-2025-65621
- https://github.com/grokability/snipe-it
- https://github.com/grokability/snipe-it/releases/tag/v8.3.4
- http://snipeitapp.com
