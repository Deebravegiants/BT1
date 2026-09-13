# [C] Improper Input Validation in httpx

## Summary
Severity: Critical
Advisory: GHSA-h8pj-cxx2-jfg2
CVE: CVE-2021-41945
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-04-29
Source: https://github.com/advisories/GHSA-h8pj-cxx2-jfg2
Type: github-advisory

## Affected
- PyPI: `httpx` — affected >=0 <0.23.0

## Details
Encode OSS httpx <=1.0.0.beta0 is affected by improper input validation in `httpx.URL`, `httpx.Client` and some functions using `httpx.URL.copy_with`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41945
- https://github.com/encode/httpx/issues/2184
- https://github.com/encode/httpx/pull/2185
- https://github.com/encode/httpx/pull/2185/commits/e3c495a32c63d8aa7f1bcf3b7b27ee1a0ff428e1
- https://github.com/encode/httpx/commit/e9b0c85dd4f4e4469c57c4b38e5101fd12081b5c
- https://gist.github.com/lebr0nli/4edb76bbd3b5ff993cf44f2fbce5e571
- https://github.com/advisories/GHSA-h8pj-cxx2-jfg2
- https://github.com/encode/httpx
- https://github.com/encode/httpx/discussions/1831
- https://github.com/encode/httpx/releases/tag/0.23.0
- https://github.com/pypa/advisory-database/tree/main/vulns/httpx/PYSEC-2022-183.yaml
- http://encode.com
