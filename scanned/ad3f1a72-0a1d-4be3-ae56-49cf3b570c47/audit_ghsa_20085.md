# [C] PaddlePaddle Out-of-bounds Read vulnerability

## Summary
Severity: Critical
Advisory: GHSA-2hvc-hwg3-hpvw
CVE: CVE-2022-46741
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-12-07
Source: https://github.com/advisories/GHSA-2hvc-hwg3-hpvw
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.4

## Details
Out-of-bounds read in `gather_tree` in PaddlePaddle before 2.4. A [patch](https://github.com/PaddlePaddle/Paddle/commit/6712e262fc6734873cc6d5ca4f45973339a88697) is available in the `release/2.4` branch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46741
- https://github.com/PaddlePaddle/Paddle/pull/47051
- https://github.com/PaddlePaddle/Paddle/commit/6712e262fc6734873cc6d5ca4f45973339a88697
- https://github.com/PaddlePaddle/Paddle/commit/ee6e6d511f9f33fc862c11722701fb5abb99ed94
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2022-001.md
