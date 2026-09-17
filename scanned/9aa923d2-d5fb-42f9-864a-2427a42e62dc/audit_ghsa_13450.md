# [C] Command injection in PaddlePaddle

## Summary
Severity: Critical
Advisory: GHSA-9q9v-qgwx-84mr
CVE: CVE-2023-38673
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-9q9v-qgwx-84mr
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.5.0

## Details
PaddlePaddle before 2.5.0 has a command injection in fs.py. This resulted in the ability to execute arbitrary commands on the operating system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38673
- https://github.com/PaddlePaddle/Paddle/commit/2bfe358043096fdba9e2a4cf0f5740102b37fd8f
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-005.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2023-126.yaml
