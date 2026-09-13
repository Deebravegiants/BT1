# [C] PaddlePaddle vulnerable to Code Injection

## Summary
Severity: Critical
Advisory: GHSA-gcjf-29m9-888q
CVE: CVE-2022-46742
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-07
Source: https://github.com/advisories/GHSA-gcjf-29m9-888q
Type: github-advisory

## Affected
- PyPI: `paddlepaddle` — affected >=0 <2.4.0

## Details
Code injection in `paddle.audio.functional.get_window` in PaddlePaddle 2.4.0-rc0 allows arbitrary code execution. A [patch](https://github.com/PaddlePaddle/Paddle/commit/26c419ca386aeae3c461faf2b828d00b48e908eb) is available on the `develop` branch of the repository and anticipated to be part of a 2.4 release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46742
- https://github.com/PaddlePaddle/Paddle/pull/47386
- https://github.com/PaddlePaddle/Paddle/commit/26c419ca386aeae3c461faf2b828d00b48e908eb
- https://github.com/PaddlePaddle/Paddle
- https://github.com/PaddlePaddle/Paddle/blob/develop/security/advisory/pdsa-2022-002.md
- https://github.com/pypa/advisory-database/tree/main/vulns/paddlepaddle/PYSEC-2022-43063.yaml
