# [H] Pytorch use-after-free vulnerability

## Summary
Severity: High
Advisory: GHSA-pg7h-5qx3-wjr3
CVE: CVE-2024-31583
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-pg7h-5qx3-wjr3
Type: github-advisory

## Affected
- PyPI: `torch` — affected >=0 <2.2.0

## Details
Pytorch before version v2.2.0 was discovered to contain a use-after-free vulnerability in torch/csrc/jit/mobile/interpreter.cpp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31583
- https://github.com/pytorch/pytorch/commit/9c7071b0e324f9fb68ab881283d6b8d388a4bcd2
- https://gist.github.com/1047524396/43e19a41f2b36503a4a228c32cdbc176
- https://github.com/pypa/advisory-database/tree/main/vulns/torch/PYSEC-2024-251.yaml
- https://github.com/pytorch/pytorch
- https://github.com/pytorch/pytorch/blob/v2.1.2/torch/csrc/jit/mobile/interpreter.cpp#L132
- https://security.snyk.io/vuln/SNYK-PYTHON-TORCH-6619806
