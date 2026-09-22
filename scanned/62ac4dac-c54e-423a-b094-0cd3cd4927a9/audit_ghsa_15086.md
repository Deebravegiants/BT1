# [M] PaddlePaddle segfault in paddle.put_along_axis

## Summary
Severity: Medium
Advisory: GHSA-2wcj-qr76-9768
CVE: CVE-2023-52303
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-2wcj-qr76-9768
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.6.0

## Details
Nullptr in paddle.put_along_axis in PaddlePaddle before 2.6.0. This flaw can cause a runtime crash and a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-52303
- https://github.com/PaddlePaddle/Paddle/commit/19da5c0c4d8c5e4dfef2a92e24141c3f51884dcc
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2023-012.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2024-135.yaml
