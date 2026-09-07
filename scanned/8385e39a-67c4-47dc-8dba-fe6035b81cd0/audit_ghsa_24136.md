# [M] Craft CMS XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9mcw-mwxv-grwj
CVE: CVE-2017-8384
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9mcw-mwxv-grwj
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0 <2.6.2976

## Details
Craft CMS before 2.6.2976 allows XSS attacks because an array returned by HttpRequestService::getSegments() and getActionSegments() need not be zero-based. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-8052.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8384
- https://craftcms.com/changelog#2-6-2976
- https://github.com/craftcms/cms
- https://twitter.com/CraftCMS/status/857743080224473088
