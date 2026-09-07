# [H] Cross-site scripting vulnerability in file upload

## Summary
Severity: High
Advisory: GHSA-hgjr-632x-qpp3
CVE: CVE-2021-39136
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-hgjr-632x-qpp3
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.5.1

## Details
There is a cross-site scripting vulnerability in file upload on the management system of baserCMS.

This is a vulnerability that needs to be addressed when the management system is used by an unspecified number of users.
If you are eligible, please update to the new version as soon as possible.

### Target
baserCMS 4.5.1 and earlier versions

### Vulnerability
Execution of malicious JavaScript code may alter the display of the page or leak cookie information.

### Countermeasures
Update to the latest version of baserCMS

Please refer to the next page for details.
https://basercms.net/security/JVN_14134801

## References
- https://github.com/baserproject/basercms/security/advisories/GHSA-hgjr-632x-qpp3
- https://nvd.nist.gov/vuln/detail/CVE-2021-39136
- https://github.com/baserproject/basercms/commit/568d4cab5ba1cdee7bbf0133c676d02a98f6d7bc
- https://basercms.net/security/JVN_14134801
- https://github.com/baserproject/basercms
- http://jvn.jp/en/jp/JVN14134801/index.html
