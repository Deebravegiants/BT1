# [M] JATOS ZIP ZipUtil.java ZipUtil path traversal

## Summary
Severity: Medium
Advisory: CVE-2022-4878
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-01-06
Source: https://osv.dev/vulnerability/CVE-2022-4878
Type: osv

## Details
A vulnerability classified as critical has been found in JATOS. Affected is the function ZipUtil of the file modules/common/app/utils/common/ZipUtil.java of the component ZIP Handler. The manipulation leads to path traversal. Upgrading to version 3.7.5-alpha is able to address this issue. The name of the patch is 2b42519f309d8164e8811392770ce604cdabb5da. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-217548.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4878.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4878
- https://vuldb.com/?id.217548
- https://vuldb.com/?ctiid.217548
- https://github.com/JATOS/JATOS/commit/2b42519f309d8164e8811392770ce604cdabb5da
- https://github.com/JATOS/JATOS/releases/tag/v3.7.5-alpha
