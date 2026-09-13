# [H] PyTorch heap buffer overflow vulnerability

## Summary
Severity: High
Advisory: GHSA-5pcm-hx3q-hm94
CVE: CVE-2024-31580
CWE: CWE-122
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-5pcm-hx3q-hm94
Type: github-advisory

## Affected
- PyPI: `torch` — affected >=0 <2.2.0

## Details
PyTorch before v2.2.0 was discovered to contain a heap buffer overflow vulnerability in the component /runtime/vararg_functions.cpp. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31580
- https://github.com/pytorch/pytorch/commit/b5c3a17c2c207ebefcb85043f0cf94be9b2fef81
- https://gist.github.com/1047524396/038c78f2f007345e6f497698ace2aa3d
- https://github.com/pypa/advisory-database/tree/main/vulns/torch/PYSEC-2024-252.yaml
- https://github.com/pytorch/pytorch
- https://security.snyk.io/vuln/SNYK-PYTHON-TORCH-6649934
