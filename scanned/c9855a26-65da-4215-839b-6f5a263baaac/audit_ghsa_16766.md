# [C] pywasm3 contains a heap buffer overflow which leads to segmentation fault

## Summary
Severity: Critical
Advisory: GHSA-mq9p-qw76-q6h7
CVE: CVE-2024-34249
CWE: CWE-122
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-06
Source: https://github.com/advisories/GHSA-mq9p-qw76-q6h7
Type: github-advisory

## Affected
- PyPI: `pywasm3` — affected >=0

## Details
wasm3 v0.5.0 was discovered to contain a heap buffer overflow which leads to segmentation fault via the function "DeallocateSlot" in wasm3/source/m3_compile.c.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34249
- https://github.com/wasm3/wasm3/issues/485
- https://github.com/pypa/advisory-database/tree/main/vulns/pywasm3/PYSEC-2024-308.yaml
- https://github.com/wasm3/pywasm3
- https://github.com/wasm3/pywasm3/blob/main/wasm3/m3_compile.c#L420
