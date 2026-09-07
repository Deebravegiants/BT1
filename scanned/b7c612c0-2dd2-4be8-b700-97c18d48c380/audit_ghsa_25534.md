# [M] TYPO3 is vulnerable to Session Fixation

## Summary
Severity: Medium
Advisory: GHSA-gqmh-5xmq-3fhg
CVE: CVE-2010-3671
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-gqmh-5xmq-3fhg
Type: github-advisory

## Affected
- Packagist: `typo3/cms-install` — affected >=0 <4.1.14
- Packagist: `typo3/cms-install` — affected >=4.2.0 <4.2.13
- Packagist: `typo3/cms-install` — affected >=4.3.0 <4.3.4
- Packagist: `typo3/cms-install` — affected >=4.4.0 <4.4.1

## Details
TYPO3 before 4.1.14, 4.2.x before 4.2.13, 4.3.x before 4.3.4 and 4.4.x before 4.4.1 is open to a session fixation attack which allows remote attackers to hijack a victim's session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3671
- https://github.com/TYPO3/typo3/commit/199cc2d53747d76657d7aab612c6b3f728d0f15d
- https://github.com/TYPO3/typo3/commit/1d649976e1f1bda684cdc7120e9f74a543059181
- https://github.com/TYPO3/typo3/commit/d3577c8e2c49122c4ab5955c70688ee441d06f23
- https://github.com/TYPO3/typo3/commit/ef3676281b0346644041a93fcbaa7bd9844bbbc5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=590719
- https://github.com/TYPO3-CMS/install
- https://security-tracker.debian.org/tracker/CVE-2010-3671
- https://typo3.org/security/advisory/typo3-sa-2010-012/#Broken_Authentication_and_Session_Management
