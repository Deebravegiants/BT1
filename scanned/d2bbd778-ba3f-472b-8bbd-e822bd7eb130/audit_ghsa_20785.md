# [H] WASM3 Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-crf8-h2wq-2h9x
CVE: CVE-2022-39974
CWE: CWE-119, CWE-20
Ecosystem: PyPI, crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-crf8-h2wq-2h9x
Type: github-advisory

## Affected
- PyPI: `pywasm3` — affected >=0
- crates.io: `wasm3` — affected >=0

## Details
WASM3 v0.5.0 was discovered to contain a segmentation fault via the component `op_Select_i32_srs` in `wasm3/source/m3_exec.h`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-39974
- https://github.com/wasm3/wasm3/issues/344
- https://github.com/wasm3/wasm3/issues/379
- https://github.com/pypa/advisory-database/tree/main/vulns/pywasm3/PYSEC-2022-43058.yaml
- https://github.com/wasm3/wasm3
