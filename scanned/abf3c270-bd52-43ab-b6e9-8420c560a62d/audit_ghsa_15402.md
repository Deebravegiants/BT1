# [M] FeehiCMS User[avatar]  unrestricted upload

## Summary
Severity: Medium
Advisory: GHSA-xp68-7g33-f49m
CVE: CVE-2024-8296
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-xp68-7g33-f49m
Type: github-advisory

## Affected
- Packagist: `feehi/cms` — affected >=0

## Details
A vulnerability was found in FeehiCMS up to 2.1.1 and classified as critical. This issue affects the function insert of the file /admin/index.php?r=user%2Fcreate. The manipulation of the argument User[avatar] leads to unrestricted upload. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8296
- https://gitee.com/A0kooo/cve_article/blob/master/feehi_cms/file_upload3/Fichkems%20user%20file%20upload%20vulnerability.md
- https://github.com/liufee/cms
- https://vuldb.com/?ctiid.276071
- https://vuldb.com/?id.276071
- https://vuldb.com/?submit.394568
