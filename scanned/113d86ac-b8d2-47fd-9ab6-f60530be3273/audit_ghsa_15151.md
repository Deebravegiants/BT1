# [M] PaddlePaddle floating point exception in paddle.argmin and paddle.argmax

## Summary
Severity: Medium
Advisory: GHSA-275c-w5mq-v5m2
CVE: CVE-2023-52313
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-275c-w5mq-v5m2
Type: github-advisory

## Affected
- PyPI: `PaddlePaddle` — affected >=0 <2.6.0

## Details
FPE in paddle.argmin and paddle.argmax in PaddlePaddle before 2.6.0. This flaw can cause a runtime crash and a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52313
- https://github.com/PaddlePaddle/Paddle/commit/6ef71779197ad6faf51ac295022ab5008d81372f
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-022.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-145.yaml
