# [C] PaddlePaddle command injection in _wget_download

## Summary
Severity: Critical
Advisory: GHSA-rf7p-79xq-8xwm
CVE: CVE-2023-52311
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-rf7p-79xq-8xwm
Type: github-advisory

## Affected
- PyPI: `PaddlePaddle` — affected >=0 <2.6.0

## Details
PaddlePaddle before 2.6.0 has a command injection in _wget_download. This resulted in the ability to execute arbitrary commands on the operating system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52311
- https://github.com/PaddlePaddle/Paddle/commit/c5f6862d118d7d69210f0e73bea1b055f5f21f2b
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-020.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-143.yaml
