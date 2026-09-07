# [M] CakePHP Authentication: Open redirect weakness via backslash bypass

## Summary
Severity: Medium
Advisory: GHSA-hhpq-7wg4-36jm
CVE: CVE-2026-55590
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-hhpq-7wg4-36jm
Type: github-advisory

## Affected
- Packagist: `cakephp/authentication` — affected >=3.0.0 <3.3.6
- Packagist: `cakephp/authentication` — affected >=4.0.0 <4.1.1
- Packagist: `cakephp/authentication` — affected >=0 <2.11.1

## Details
### Impact
The `getLoginRedirect()` method contains a weakness to backslash bypasses allowing redirect targets with attacker controlled hostnames.

### Patches
2.11.1, 3.3.6 and 4.1.1 contain a fix for this issue.

### Workarounds
If you are unable to upgrade, you should consider adding application validation to the redirect query string parameter to mitigate this vulnerability.

## References
- https://github.com/cakephp/authentication/security/advisories/GHSA-hhpq-7wg4-36jm
- https://nvd.nist.gov/vuln/detail/CVE-2026-55590
- https://github.com/cakephp/authentication/pull/795
- https://github.com/cakephp/authentication/pull/796
- https://github.com/cakephp/authentication/pull/799
- https://github.com/cakephp/authentication/commit/1c1e29c7e8129cfbcae74558316ecd3ea50a8273
- https://github.com/cakephp/authentication/commit/df28ea4e712f1e5bd0e42be4a3c5c750ca50764d
- https://github.com/cakephp/authentication/commit/ee24bd48b9c3ef693dc9965de8f0cc8020a7052c
- https://github.com/cakephp/authentication
- https://github.com/cakephp/authentication/releases/tag/2.11.1
- https://github.com/cakephp/authentication/releases/tag/3.3.6
- https://github.com/cakephp/authentication/releases/tag/4.1.1
