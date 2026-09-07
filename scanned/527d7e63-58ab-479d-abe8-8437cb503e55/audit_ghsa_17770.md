# [H] TYPO3 Scheduler Module vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-7835-fcv3-g256
CVE: CVE-2024-55924
CWE: CWE-352, CWE-749
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-7835-fcv3-g256
Type: github-advisory

## Affected
- Packagist: `typo3/cms-scheduler` — affected >=11.0.0 <11.5.42

## Details
### Problem
A vulnerability has been identified in the backend user interface functionality involving deep links. Specifically, this functionality is susceptible to Cross-Site Request Forgery (CSRF). Additionally, state-changing actions in downstream components incorrectly accepted submissions via HTTP GET and did not enforce the appropriate HTTP method.

Successful exploitation of this vulnerability requires the victim to have an active session on the backend user interface and to be deceived into interacting with a malicious URL targeting the backend, which can occur under the following conditions:

* the user opens a malicious link, such as one sent via email.
* the user visits a compromised or manipulated website while the following settings are misconfigured:
  + `security.backend.enforceReferrer` feature is disabled,
  + `BE/cookieSameSite` configuration is set to `lax` or `none`

The vulnerability in the affected downstream component “Scheduler Module” allows attackers to trigger pre-defined command classes - which can lead to unauthorized import or export of data in the worst case.

### Solution
Update to TYPO3 versions 11.5.42 ELTS that fixes the problem described.

### Credits
Thanks to Gabriel Dimitrov who reported this issue and to TYPO3 core and security members Benjamin Franzke, Oliver Hader, Andreas Kienast, Torben Hansen, Elias Häußler who fixed the issue.

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-7835-fcv3-g256
- https://nvd.nist.gov/vuln/detail/CVE-2024-55924
- https://github.com/TYPO3-CMS/scheduler
- https://typo3.org/security/advisory/typo3-core-sa-2025-009
