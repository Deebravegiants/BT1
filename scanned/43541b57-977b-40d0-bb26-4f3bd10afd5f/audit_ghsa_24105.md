# [H] blosc2 heap-based buffer overflow

## Summary
Severity: High
Advisory: GHSA-8c7c-2c8j-3xfp
CVE: CVE-2020-29367
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8c7c-2c8j-3xfp
Type: github-advisory

## Affected
- PyPI: `blosc2` — affected >=0 <0.1.7

## Details
blosc2.c in Blosc C-Blosc2 through 2.0.0.beta.5 has a heap-based buffer overflow when there is a lack of space to write compressed data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29367
- https://github.com/Blosc/c-blosc2/commit/c4c6470e88210afc95262c8b9fcc27e30ca043ee
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26442
- https://github.com/Blosc/python-blosc2
- https://github.com/Blosc/python-blosc2/releases/tag/v0.1.7
- https://github.com/pypa/advisory-database/tree/main/vulns/blosc2/PYSEC-2020-343.yaml
