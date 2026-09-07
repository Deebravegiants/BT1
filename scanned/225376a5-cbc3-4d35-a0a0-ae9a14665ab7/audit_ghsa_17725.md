# [M] TYPO3 Cross-Site Request Forgery in Dashboard Module

## Summary
Severity: Medium
Advisory: GHSA-qwx7-39pw-2mhr
CVE: CVE-2024-55920
CWE: CWE-352, CWE-749
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-qwx7-39pw-2mhr
Type: github-advisory

## Affected
- Packagist: `typo3/cms-dashboard` — affected >=10.0.0 <10.4.48
- Packagist: `typo3/cms-dashboard` — affected >=11.0.0 <11.5.42
- Packagist: `typo3/cms-dashboard` — affected >=12.0.0 <12.4.25
- Packagist: `typo3/cms-dashboard` — affected >=13.0.0 <13.4.3

## Details
### Problem
A vulnerability has been identified in the backend user interface functionality involving deep links. Specifically, this functionality is susceptible to Cross-Site Request Forgery (CSRF). Additionally, state-changing actions in downstream components incorrectly accepted submissions via HTTP GET and did not enforce the appropriate HTTP method.

Successful exploitation of this vulnerability requires the victim to have an active session on the backend user interface and to be deceived into interacting with a malicious URL targeting the backend, which can occur under the following conditions:

* the user opens a malicious link, such as one sent via email.
* the user visits a compromised or manipulated website while the following settings are misconfigured:
  + `security.backend.enforceReferrer` feature is disabled,
  + `BE/cookieSameSite` configuration is set to `lax` or `none`

The vulnerability in the affected downstream component “Dashboard Module” allows attackers to manipulate the victim’s dashboard configuration.

### Solution
Update to TYPO3 versions 11.5.42 ELTS, 12.4.25 LTS, 13.4.3 LTS that fix the problem described.

### Credits
Thanks to TYPO3 core and security members Benjamin Franzke, Oliver Hader, Andreas Kienast, Torben Hansen, Elias Häußler who fixed the issue.

### References
* [TYPO3-CORE-SA-2025-005](https://typo3.org/security/advisory/typo3-core-sa-2025-005)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-qwx7-39pw-2mhr
- https://nvd.nist.gov/vuln/detail/CVE-2024-55920
- https://github.com/TYPO3-CMS/dashboard/commit/c2e5dbdda87387ad9ee2ff8ca986d41dd9424875
- https://github.com/TYPO3-CMS/dashboard
- https://typo3.org/security/advisory/typo3-core-sa-2025-005
