# [H] ydata unsafe deserialization

## Summary
Severity: High
Advisory: GHSA-cg49-hrj4-3rpr
CVE: CVE-2024-37064
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-cg49-hrj4-3rpr
Type: github-advisory

## Affected
- PyPI: `ydata-profiling` — affected >=3.7.0

## Details
Deseriliazation of untrusted data can occur in versions 3.7.0 or newer of Ydata's ydata-profiling open-source library, enabling a maliciously crafted dataset to run arbitrary code on an end user's system when loaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37064
- https://github.com/ydataai/ydata-profiling
- https://hiddenlayer.com/sai-security-advisory/ydata-june2024
