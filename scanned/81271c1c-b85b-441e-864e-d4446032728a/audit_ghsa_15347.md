# [M] FeehiCMS BannerForm[img] unrestricted upload

## Summary
Severity: Medium
Advisory: GHSA-3wrg-6mg5-jg2v
CVE: CVE-2024-8295
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-3wrg-6mg5-jg2v
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0

## Details
A vulnerability has been found in FeehiCMS up to 2.1.1 and classified as critical. This vulnerability affects the function createBanner of the file /admin/index.php?r=banner%2Fbanner-create. The manipulation of the argument BannerForm[img] leads to unrestricted upload. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8295
- https://gitee.com/A0kooo/cve_article/blob/master/feehi_cms/file_upload2/Fichkems%20banner%20file%20upload%20vulnerability.md
- https://github.com/liufee/cms
- https://vuldb.com/?ctiid.276070
- https://vuldb.com/?id.276070
- https://vuldb.com/?submit.394560
