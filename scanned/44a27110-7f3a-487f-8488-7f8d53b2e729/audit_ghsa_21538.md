# [C] PyTorch vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-47fc-vmwq-366v
CVE: CVE-2022-45907
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-26
Source: https://github.com/advisories/GHSA-47fc-vmwq-366v
Type: github-advisory

## Affected
- PyPI: `torch` — affected >=0 <1.13.1

## Details
In PyTorch before trunk/89695, torch.jit.annotations.parse_type_line can cause arbitrary code execution because eval is used unsafely. The fix for this issue is available in version 1.13.1. There is a release checker in [issue #89855](https://github.com/pytorch/pytorch/issues/89855).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45907
- https://github.com/pytorch/pytorch/issues/88868
- https://github.com/pytorch/pytorch/issues/89855
- https://github.com/pytorch/pytorch/pull/89189
- https://github.com/pytorch/pytorch/commit/767f6aa49fe20a2766b9843d01e3b7f7793df6a3
- https://github.com/pypa/advisory-database/tree/main/vulns/torch/PYSEC-2022-43015.yaml
- https://github.com/pytorch/pytorch
- https://github.com/pytorch/pytorch/releases/tag/v1.13.1
