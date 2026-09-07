# [M] Null pointer dereference in PaddlePaddle

## Summary
Severity: Medium
Advisory: GHSA-rr46-m366-gm44
CVE: CVE-2023-38670
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-rr46-m366-gm44
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.5.0

## Details
Null pointer dereference in paddle.flip in PaddlePaddle before 2.5.0. This resulted in a runtime crash and denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38670
- https://github.com/PaddlePaddle/Paddle/commit/ed96baeed19b4e11b6cbc2dcc6776245ba5fab13
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-002.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2023-123.yaml
