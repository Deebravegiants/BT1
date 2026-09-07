# [M] Silverstripe CMS User Enumeration 

## Summary
Severity: Medium
Advisory: GHSA-fwhr-g5r4-xgxf
CVE: CVE-2017-12849
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fwhr-g5r4-xgxf
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=0 <3.5.5
- Packagist: `silverstripe/cms` — affected >=3.6 <3.6.1

## Details
Response discrepancy in the login and password reset forms in SilverStripe CMS before 3.5.5 and 3.6.x before 3.6.1 allows remote attackers to enumerate users via timing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12849
- https://www.silverstripe.org/download/security-releases/ss-2017-005
