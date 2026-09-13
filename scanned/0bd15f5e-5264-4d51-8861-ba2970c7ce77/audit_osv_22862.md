# [M] GPAC SVG Parser svg_attributes.c svg_parse_preserveaspectratio memory leak

## Summary
Severity: Medium
Advisory: CVE-2022-3957
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2022-11-11
Source: https://osv.dev/vulnerability/CVE-2022-3957
Type: osv

## Details
A vulnerability classified as problematic was found in GPAC. Affected by this vulnerability is the function svg_parse_preserveaspectratio of the file scenegraph/svg_attributes.c of the component SVG Parser. The manipulation leads to memory leak. The attack can be launched remotely. The name of the patch is 2191e66aa7df750e8ef01781b1930bea87b713bb. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-213463.

## References
- https://vuldb.com/?id.213463
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3957.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3957
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/2191e66aa7df750e8ef01781b1930bea87b713bb
