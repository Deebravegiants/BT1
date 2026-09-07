# [H] Improper escaping of command arguments on Windows leading to command injection

## Summary
Severity: High
Advisory: GHSA-frqg-7g38-6gcf
CVE: CVE-2021-41116
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-10-05
Source: https://github.com/advisories/GHSA-frqg-7g38-6gcf
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=0 <1.10.23
- Packagist: `composer/composer` — affected >=2.0.0-alpha1 <2.1.9

## Details
### Impact
Windows users running Composer to install untrusted dependencies are affected and should definitely upgrade for safety. Other OSs and WSL are not affected. 

### Patches
1.10.23 and 2.1.9 fix the issue

### Workarounds
None

## References
- https://github.com/composer/composer/security/advisories/GHSA-frqg-7g38-6gcf
- https://nvd.nist.gov/vuln/detail/CVE-2021-41116
- https://github.com/composer/composer/commit/ca5e2f8d505fd3bfac6f7c85b82f2740becbc0aa
- https://github.com/FriendsOfPHP/security-advisories/blob/master/composer/composer/CVE-2021-41116.yaml
- https://github.com/composer/composer
- https://www.sonarsource.com/blog/securing-developer-tools-package-managers
- https://www.tenable.com/security/tns-2022-09
