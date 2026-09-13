# [H] ydata unsafe deserialization

## Summary
Severity: High
Advisory: GHSA-fpvj-m2h6-6wc5
CVE: CVE-2024-37062
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-fpvj-m2h6-6wc5
Type: github-advisory

## Affected
- PyPI: `ydata-profiling` — affected >=3.7.0

## Details
Deserialization of untrusted data can occur in versions 3.7.0 or newer of Ydata's ydata-profiling open-source library, enabling a malicously crafted report to run arbitrary code on an end user's system when loaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37062
- https://github.com/ydataai/ydata-profiling
- https://hiddenlayer.com/sai-security-advisory/ydata-june2024
