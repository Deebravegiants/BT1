# [M] Femanager extension for TYPO3 allows Insecure Direct Object Reference

## Summary
Severity: Medium
Advisory: GHSA-rc5f-3hfv-jxp2
CVE: CVE-2025-7900
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-22
Source: https://github.com/advisories/GHSA-rc5f-3hfv-jxp2
Type: github-advisory

## Affected
- Packagist: `in2code/femanager` — affected >=0 <6.4.2
- Packagist: `in2code/femanager` — affected >=7.0.0 <7.5.3
- Packagist: `in2code/femanager` — affected >=8.0.0 <8.3.1

## Details
The femanager extension for TYPO3 allows Insecure Direct Object Reference resulting in unauthorized modification of userdata. This issue affects femanager version 6.4.1 and below, 7.0.0 to 7.5.2 and 8.0.0 to 8.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-7900
- https://github.com/in2code-de/femanager/commit/9bd9fbded4cf31f69bfe03c55d406e79050f8069
- https://github.com/in2code-de/femanager
- https://typo3.org/security/advisory/typo3-ext-sa-2025-010
