# [M] events2 TYPO3 extension insecure direct object reference (IDOR) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cchp-3rq6-69wj
CVE: CVE-2024-38874
CWE: CWE-639, CWE-693
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-06-21
Source: https://github.com/advisories/GHSA-cchp-3rq6-69wj
Type: github-advisory

## Affected
- Packagist: `jweiland/events2` — affected >=0 <8.3.8
- Packagist: `jweiland/events2` — affected >=9.0.0 <9.0.6

## Details
An issue was discovered in the events2 (aka Events 2) extension before 8.3.8 and 9.x before 9.0.6 for TYPO3. Missing access checks in the management plugin lead to an insecure direct object reference (IDOR) vulnerability with the potential to activate or delete various events for unauthenticated users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38874
- https://github.com/FriendsOfPHP/security-advisories/blob/master/jweiland/events2/CVE-2024-38874.yaml
- https://github.com/jweiland-net/events2
- https://typo3.org/security/advisory/typo3-ext-sa-2024-003
