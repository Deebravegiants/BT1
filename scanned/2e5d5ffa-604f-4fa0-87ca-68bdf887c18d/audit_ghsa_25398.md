# [C] Silverstripe Framework SQLi Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wvfw-w3x6-g526
CVE: CVE-2019-5715
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wvfw-w3x6-g526
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.0.0 <3.6.7
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.0.7
- Packagist: `silverstripe/framework` — affected >=3.7.0 <3.7.3
- Packagist: `silverstripe/framework` — affected >=4.1.0 <4.1.5
- Packagist: `silverstripe/framework` — affected >=4.2.0 <4.2.4
- Packagist: `silverstripe/framework` — affected >=4.3.0 <4.3.1

## Details
All versions of SilverStripe 3 prior to 3.6.7 and 3.7.3, and all versions of SilverStripe 4 prior to 4.0.7, 4.1.5, 4.2.4, and 4.3.1 allows Reflected SQL Injection through Form and DataObject.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5715
- https://github.com/silverstripe/silverstripe-framework/issues/8814
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2019-5715.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/ss-2018-021
