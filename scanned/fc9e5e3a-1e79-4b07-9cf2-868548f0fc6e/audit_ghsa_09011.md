# [M] Funadmin has an Improper Access Control Issue

## Summary
Severity: Medium
Advisory: GHSA-qhh7-263p-54r3
CVE: CVE-2026-7733
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-qhh7-263p-54r3
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
A flaw has been found in funadmin up to 7.1.0-rc6. This affects the function UploadService::chunkUpload of the file app/common/service/UploadService.php of the component Frontend Chunked Upload Endpoint. This manipulation of the argument File causes unrestricted upload. The attack is possible to be carried out remotely. The exploit has been published and may be used. Patch name: 59. To fix this issue, it is recommended to deploy a patch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7733
- https://gitee.com/funadmin/funadmin
- https://gitee.com/funadmin/funadmin/issues/IJ8NXT
- https://gitee.com/funadmin/funadmin/pulls/59
- https://vuldb.com/submit/807559
- https://vuldb.com/vuln/360908
- https://vuldb.com/vuln/360908/cti
