# [M] Backdrop CMS Host Header Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ffpg-gm3h-4p5p
CVE: CVE-2025-63828
CWE: CWE-601, CWE-644
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N/E:P (CVSS_V4)
Published: 2025-11-18
Source: https://github.com/advisories/GHSA-ffpg-gm3h-4p5p
Type: github-advisory

## Affected
- Packagist: `backdrop/backdrop` — affected >=0

## Details
Host Header Injection vulnerability in Backdrop CMS 1.32.1 allows attackers to manipulate the Host header in password reset requests, leading to redirects to malicious domains and potential session hijacking via cookie injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-63828
- https://github.com/backdrop/backdrop
- https://github.com/mertdurum06/BackdropCms-1.32.1
- https://github.com/mertdurum06/BackdropCms-1.32.1/blob/main/backdropcms_exploit.txt
