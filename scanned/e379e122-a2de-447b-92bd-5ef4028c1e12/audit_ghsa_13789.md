# [M] Symfony potential Cross-site Scripting in WebhookController

## Summary
Severity: Medium
Advisory: GHSA-72x2-5c85-6wmr
CVE: CVE-2023-46735
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-12
Source: https://github.com/advisories/GHSA-72x2-5c85-6wmr
Type: github-advisory

## Affected
- Packagist: `symfony/webhook` — affected >=6.3.0 <6.3.8
- Packagist: `symfony/symfony` — affected >=6.3.0 <6.3.8

## Details
### Description

The error message in WebhookController returns unescaped user-submitted input.

### Resolution

WebhookController now doesn't return any user-submitted input in its response.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/8128c302430394f639e818a7103b3f6815d8d962) for branch 6.3.

### Credits

We would like to thank Maxime Aknin for reporting the issue and to Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-72x2-5c85-6wmr
- https://nvd.nist.gov/vuln/detail/CVE-2023-46735
- https://github.com/symfony/symfony/commit/8128c302430394f639e818a7103b3f6815d8d962
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2023-46735.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2023-46735
