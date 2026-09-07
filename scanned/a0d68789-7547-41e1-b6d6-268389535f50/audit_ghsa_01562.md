# [H] Missing Required Cryptographic Step Leading to Sensitive Information Disclosure in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-m5vr-3m74-jwxp
CVE: CVE-2020-15098
CWE: CWE-20, CWE-200, CWE-325, CWE-327, CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-m5vr-3m74-jwxp
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.20
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.6
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.6
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.20

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C` (8.2)
> * CWE-325, CWE-20, CWE-200, CWE-502

### Problem
It has been discovered that an internal verification mechanism can be used to generate arbitrary checksums. This allows to inject arbitrary data having a valid cryptographic message authentication code (HMAC-SHA1) and can lead to various attack chains as described below.

* [TYPO3-CORE-SA-2020-007](https://typo3.org/security/advisory/typo3-core-sa-2020-007), [CVE-2020-15099](https://nvd.nist.gov/vuln/detail/CVE-2020-15099): Potential Privilege Escalation
  + the database server used for a TYPO3 installation must be accessible for an attacker (either via internet or shared hosting network)
  + `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C` (7.5, high)
* [TYPO3-CORE-SA-2016-013](https://typo3.org/security/advisory/typo3-core-sa-2016-013), [CVE-2016-5091](https://nvd.nist.gov/vuln/detail/CVE-2016-5091): Insecure Deserialization & Remote Code Execution
  + an attacker must have access to at least one Extbase plugin or module action in a TYPO3 installation
  + `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C` (9.1, critical)

The overall severity of this vulnerability is **high (8.2)** based on mentioned attack chains and the requirement of having a valid backend user session (authenticated).

### Solution
Update to TYPO3 versions 9.5.20 or 10.4.6 that fix the problem described.

### Credits
Thanks to TYPO3 security team member Oliver Hader who reported and fixed the issue.

### References
* [TYPO3-CORE-SA-2020-008](https://typo3.org/security/advisory/typo3-core-sa-2020-008)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-m5vr-3m74-jwxp
- https://nvd.nist.gov/vuln/detail/CVE-2016-5091
- https://nvd.nist.gov/vuln/detail/CVE-2020-15098
- https://github.com/TYPO3/TYPO3.CMS/commit/85d3e70dff35a99ef53f4b561114acfa9e5c47e1
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-15098.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-15098.yaml
- https://github.com/TYPO3/TYPO3.CMS
- https://typo3.org/security/advisory/typo3-core-sa-2016-013
- https://typo3.org/security/advisory/typo3-core-sa-2020-008
