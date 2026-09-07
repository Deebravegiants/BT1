# [M] TYPO3 DB Check Module vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-8mv3-37rc-pvxj
CVE: CVE-2024-55945
CWE: CWE-352, CWE-749
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-8mv3-37rc-pvxj
Type: github-advisory

## Affected
- Packagist: `typo3/cms-lowlevel` — affected >=11.0.0 <11.5.42

## Details
### Problem
A vulnerability has been identified in the backend user interface functionality involving deep links. Specifically, this functionality is susceptible to Cross-Site Request Forgery (CSRF). Additionally, state-changing actions in downstream components incorrectly accepted submissions via HTTP GET and did not enforce the appropriate HTTP method.

Successful exploitation of this vulnerability requires the victim to have an active session on the backend user interface and to be deceived into interacting with a malicious URL targeting the backend, which can occur under the following conditions:

* the user opens a malicious link, such as one sent via email.
* the user visits a compromised or manipulated website while the following settings are misconfigured:
  + `security.backend.enforceReferrer` feature is disabled,
  + `BE/cookieSameSite` configuration is set to `lax` or `none`

The vulnerability in the affected downstream component “DB Check Module” allows attackers to manipulate data through unauthorized actions.

### Solution
Update to TYPO3 versions 11.5.42 ELTS that fixes the problem described.

### Credits
Thanks to Gabriel Dimitrov who reported this issue and to TYPO3 core and security members Benjamin Franzke, Oliver Hader, Andreas Kienast, Torben Hansen, Elias Häußler who fixed the issue.

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-8mv3-37rc-pvxj
- https://nvd.nist.gov/vuln/detail/CVE-2024-55945
- https://github.com/TYPO3-CMS/lowlevel
- https://typo3.org/security/advisory/typo3-core-sa-2025-010
