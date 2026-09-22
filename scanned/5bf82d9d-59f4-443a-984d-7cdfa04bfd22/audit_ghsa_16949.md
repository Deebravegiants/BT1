# [M] Mautic SQL Injection in dynamic Reports

## Summary
Severity: Medium
Advisory: GHSA-jj6w-2cqg-7p94
CVE: CVE-2022-25775
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-jj6w-2cqg-7p94
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=2.14.1 <4.4.12
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.0.4

## Details
### Impact
Prior to the patched version, logged in users of Mautic are vulnerable to an SQL injection vulnerability in the Reports bundle.

The user could retrieve and alter data like sensitive data, login, and depending on database permission the attacker can manipulate file systems.

### Patches
Update to 4.4.12 or 5.0.4

### Workarounds
No

### References
- https://owasp.org/www-community/attacks/SQL_Injection
- https://owasp.org/www-community/attacks/Blind_SQL_Injection

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-jj6w-2cqg-7p94
- https://nvd.nist.gov/vuln/detail/CVE-2022-25775
- https://github.com/mautic/mautic/commit/cab65e0acc4f23c4f07c117dee1b69dac5abed3f
- https://github.com/mautic/mautic/commit/e75b1eea16309588f069169b5882cf53f854dbd8
- https://github.com/mautic/mautic
