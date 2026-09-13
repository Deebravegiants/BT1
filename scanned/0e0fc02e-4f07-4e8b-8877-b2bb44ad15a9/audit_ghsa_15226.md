# [C] PaddlePaddle command injection in convert_shape_compare

## Summary
Severity: Critical
Advisory: GHSA-3cr5-2446-8pg3
CVE: CVE-2023-52314
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-3cr5-2446-8pg3
Type: github-advisory

## Affected
- PyPI: `PaddlePaddle` — affected >=0 <2.6.0

## Details
PaddlePaddle before 2.6.0 has a command injection in convert_shape_compare. This resulted in the ability to execute arbitrary commands on the operating system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52314
- https://github.com/PaddlePaddle/Paddle/commit/5ed9478fdef96a06eeec9093f9e768c97b094af3
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-023.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-146.yaml
