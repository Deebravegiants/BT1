# [M] FlatPress File Delete panel.mediamanager.file.php doItemActions path traversal

## Summary
Severity: Medium
Advisory: CVE-2022-4748
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2022-4748
Type: osv

## Details
A vulnerability was found in FlatPress. It has been classified as critical. This affects the function doItemActions of the file fp-plugins/mediamanager/panels/panel.mediamanager.file.php of the component File Delete Handler. The manipulation of the argument deletefile leads to path traversal. The name of the patch is 5d5c7f6d8f072d14926fc2c3a97cdd763802f170. It is recommended to apply a patch to fix this issue. The identifier VDB-216861 was assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4748.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4748
- https://vuldb.com/?id.216861
- https://github.com/flatpressblog/flatpress/issues/179
- https://vuldb.com/?ctiid.216861
- https://github.com/flatpressblog/flatpress/commit/5d5c7f6d8f072d14926fc2c3a97cdd763802f170
