# [M] Lack of access control on upoaded files

## Summary
Severity: Medium
Advisory: GHSA-jvx5-rm6q-gx7p
CVE: CVE-2019-12245
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-jvx5-rm6q-gx7p
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.6.8
- Packagist: `silverstripe/framework` — affected >=3.7.0 <3.7.4
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.3.6
- Packagist: `silverstripe/framework` — affected >=4.4.0 <4.4.4
- Packagist: `silverstripe/assets` — affected >=1.0.0 <1.3.5
- Packagist: `silverstripe/assets` — affected >=1.4.0 <1.4.4

## Details
SilverStripe through 4.3.3 has incorrect access control for protected files uploaded via Upload::loadIntoFile(). An attacker may be able to guess a filename in silverstripe/assets via the AssetControlExtension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12245
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/assets/CVE-2019-12245.yaml
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/CVE-2019-12245
- https://www.silverstripe.org/download/security-releases/cve-2019-12245
