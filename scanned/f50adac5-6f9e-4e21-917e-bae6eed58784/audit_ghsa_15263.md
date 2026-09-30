# [M] FeehiCMS  file upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xxqw-83c7-r24r
CVE: CVE-2024-8294
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-xxqw-83c7-r24r
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0

## Details
A vulnerability, which was classified as critical, was found in FeehiCMS up to 2.1.1. This affects the function update of the file /admin/index.php?r=friendly-link%2Fupdate. The manipulation of the argument FriendlyLink[image] leads to unrestricted upload. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8294
- https://gitee.com/A0kooo/cve_article/blob/master/feehi_cms/Fichkems%20Friendley-Link%20file%20upload%20vulnerability.md
- https://github.com/liufee/cms
- https://vuldb.com/?ctiid.276069
- https://vuldb.com/?id.276069
- https://vuldb.com/?submit.394556
