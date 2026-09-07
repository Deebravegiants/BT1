# [M] Insertion of Sensitive Information into Log File in typo3/cms-core

## Summary
Severity: Medium
Advisory: GHSA-fh99-4pgr-8j99
CVE: CVE-2022-31047
CWE: CWE-209, CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-fh99-4pgr-8j99
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=7.0.0 <7.6.57
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.47
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.35
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.29
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.11
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.29
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.11

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N/E:F/RL:O/RC:C` (4.9)

### Problem
It has been discovered that system internal credentials or keys (e.g. database credentials) have been logged as plaintext in exception handlers, when logging the complete exception stack trace.

### Solution
Update to TYPO3 versions 7.6.57 ELTS, 8.7.47 ELTS, 9.5.35 ELTS, 10.4.29, 11.5.11 that fix the problem described above.

### Credits
Thanks to Marco Huber who reported this issue and to TYPO3 security member Torben Hansen who fixed the issue.

### References
* [TYPO3-CORE-SA-2022-002](https://typo3.org/security/advisory/typo3-core-sa-2022-002)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-fh99-4pgr-8j99
- https://nvd.nist.gov/vuln/detail/CVE-2022-31047
- https://github.com/TYPO3/typo3/commit/c93ea692e7dfef03b7c50fe5437487545bee4d6a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-31047.yaml
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2022-002
