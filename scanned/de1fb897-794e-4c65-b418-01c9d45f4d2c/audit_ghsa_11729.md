# [C] baserCMS has OS command injection vulnerability in installer

## Summary
Severity: Critical
Advisory: GHSA-6hpg-8rx3-cwgv
CVE: CVE-2026-30880
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-6hpg-8rx3-cwgv
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <5.2.3

## Details
baserCMS has an OS command injection vulnerability in the installer.

### Target
baserCMS 5.2.2 and earlier versions

### Vulnerability

If baserCMS is placed on a server but not installed, malicious commands may be executed.

### Countermeasures
Update to the latest version of baserCMS

Please refer to the following page to reference for more information.
https://basercms.net/security/JVN_54513170

### Credits

REN XINGDIAN

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-6hpg-8rx3-cwgv
- https://nvd.nist.gov/vuln/detail/CVE-2026-30880
- https://basercms.net/security/JVN_20837860
- https://github.com/baserproject/basercms
- https://github.com/baserproject/basercms/releases/tag/5.2.3
