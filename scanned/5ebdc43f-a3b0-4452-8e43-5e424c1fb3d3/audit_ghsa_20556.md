# [M] Path Traversal in nemo-toolkit

## Summary
Severity: Medium
Advisory: GHSA-9hg3-hmmf-c3gr
CVE: CVE-2022-22821
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-01-11
Source: https://github.com/advisories/GHSA-9hg3-hmmf-c3gr
Type: github-advisory

## Affected
- PyPI: `nemo-toolkit` — affected >=0 <1.6.0

## Details
NVIDIA NeMo before 1.6.0 contains a vulnerability in ASR WebApp, in which ../ Path Traversal may lead to deletion of any directory when admin privileges are available.

## References
- https://github.com/NVIDIA/NeMo/security/advisories/GHSA-rpx7-33j2-xx9x
- https://nvd.nist.gov/vuln/detail/CVE-2022-22821
- https://github.com/NVIDIA/NeMo
