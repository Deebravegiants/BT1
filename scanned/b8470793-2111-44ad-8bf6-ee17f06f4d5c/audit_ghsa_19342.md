# [M] reint_downloadmanager TYPO3 Extension is susceptible to Insecure Direct Object Reference

## Summary
Severity: Medium
Advisory: GHSA-jjwh-4x89-7f5w
CVE: CVE-2025-48207
CWE: CWE-425, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N/E:F/RL:O/RC:C (CVSS_V3)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-jjwh-4x89-7f5w
Type: github-advisory

## Affected
- Packagist: `renolit/reint-downloadmanager` — affected >=5.0.0 <5.0.1
- Packagist: `renolit/reint-downloadmanager` — affected >=0 <4.0.2

## Details
Insecure Direct Object Reference in the reint_downloadmanager TYPO3 extension allows remote attackers to read arbitrary files via the downloaduid parameter in the downloadAction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48207
- https://github.com/Kephson/reint_downloadmanager/commit/99b07497f5842a59e934583283e1b5a477ce79a9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/renolit/reint-downloadmanager/CVE-2025-48207.yaml
- https://github.com/Kephson/reint_downloadmanager
- https://typo3.org/security/advisory/typo3-ext-sa-2025-004
