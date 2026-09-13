# [M] Float point exception (FPE) in paddlepaddle

## Summary
Severity: Medium
Advisory: GHSA-cv2j-922j-hr56
CVE: CVE-2023-38672
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-cv2j-922j-hr56
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.5.0

## Details
FPE in paddle.linalg.matrix_power in PaddlePaddle before 2.5.0. This flaw can cause a runtime crash and a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38672
- https://github.com/PaddlePaddle/Paddle/commit/09926af166b060c9a9845c309110d3baa82921fd
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-004.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2023-125.yaml
