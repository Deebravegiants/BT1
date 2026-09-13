# [M] MindSpore vulnerable to memory corruption

## Summary
Severity: Medium
Advisory: GHSA-x67g-47p3-rc7f
CVE: CVE-2023-2970
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-x67g-47p3-rc7f
Type: github-advisory

## Affected
- PyPI: `mindspore` — affected >=0

## Details
A vulnerability classified as problematic was found in MindSpore 2.0.0-alpha/2.0.0-rc1. This vulnerability affects the function `JsonHelper::UpdateArray` of the file `mindspore/ccsrc/minddata/dataset/util/json_helper.cc`. The manipulation leads to memory corruption. The name of the patch is 30f4729ea2c01e1ed437ba92a81e2fc098d608a9. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-230176.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2970
- https://gitee.com/mindspore/mindspore
- https://gitee.com/mindspore/mindspore/commit/30f4729ea2c01e1ed437ba92a81e2fc098d608a9
- https://gitee.com/mindspore/mindspore/issues/I73DOS
- https://github.com/pypa/advisory-database/tree/main/vulns/mindspore/PYSEC-2023-81.yaml
- https://vuldb.com/?ctiid.230176
- https://vuldb.com/?id.230176
