# [M] PaddlePaddle floating point exception in paddle.linalg.matrix_rank

## Summary
Severity: Medium
Advisory: GHSA-jm68-fpmr-8j2g
CVE: CVE-2023-38675
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-jm68-fpmr-8j2g
Type: github-advisory

## Affected
- PyPI: `PaddlePaddle` — affected >=0 <2.6.0

## Details
FPE in paddle.linalg.matrix_rank in PaddlePaddle before 2.6.0. This flaw can cause a runtime crash and a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38675
- https://github.com/PaddlePaddle/Paddle/commit/690ffe814dbfc5054d4e92df878687fd638fe3a5
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-007.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-130.yaml
