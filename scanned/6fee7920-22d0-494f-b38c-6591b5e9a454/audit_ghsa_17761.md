# [H] TYPO3 Extension Manager Module vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-4g52-pq8j-6qv5
CVE: CVE-2024-55921
CWE: CWE-352, CWE-749
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-4g52-pq8j-6qv5
Type: github-advisory

## Affected
- Packagist: `typo3/cms-extensionmanager` — affected >=10.0.0 <10.4.48
- Packagist: `typo3/cms-extensionmanager` — affected >=11.0.0 <11.5.42
- Packagist: `typo3/cms-extensionmanager` — affected >=12.0.0 <12.4.25
- Packagist: `typo3/cms-extensionmanager` — affected >=13.0.0 <13.4.3

## Details
### Problem
A vulnerability has been identified in the backend user interface functionality involving deep links. Specifically, this functionality is susceptible to Cross-Site Request Forgery (CSRF). Additionally, state-changing actions in downstream components incorrectly accepted submissions via HTTP GET and did not enforce the appropriate HTTP method.

Successful exploitation of this vulnerability requires the victim to have an active session on the backend user interface and to be deceived into interacting with a malicious URL targeting the backend, which can occur under the following conditions:

* the user opens a malicious link, such as one sent via email.
* the user visits a compromised or manipulated website while the following settings are misconfigured:
  + `security.backend.enforceReferrer` feature is disabled,
  + `BE/cookieSameSite` configuration is set to `lax` or `none`

The vulnerability in the affected downstream component “Extension Manager Module” allows attackers to retrieve and install 3rd party extensions from the TYPO3 Extension Repository - which can lead to remote code execution in the worst case.

### Solution
Update to TYPO3 versions 11.5.42 ELTS, 12.4.25 LTS, 13.4.3 LTS that fix the problem described.

### Credits
Thanks to TYPO3 core and security members Benjamin Franzke, Oliver Hader, Andreas Kienast, Torben Hansen, Elias Häußler who fixed the issue.

### References
* [TYPO3-CORE-SA-2025-006](https://typo3.org/security/advisory/typo3-core-sa-2025-006)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-4g52-pq8j-6qv5
- https://nvd.nist.gov/vuln/detail/CVE-2024-55921
- https://github.com/TYPO3-CMS/extensionmanager/commit/a5a58626dcb2af0c31bc6aec068e3d24e789b9e8
- https://github.com/TYPO3-CMS/extensionmanager
- https://typo3.org/security/advisory/typo3-core-sa-2025-006
