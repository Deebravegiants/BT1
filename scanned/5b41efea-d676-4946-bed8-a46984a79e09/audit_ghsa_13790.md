# [C] transmute-core unsafe YAML deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-w9cp-3x79-2p8p
CVE: CVE-2023-47204
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-02
Source: https://github.com/advisories/GHSA-w9cp-3x79-2p8p
Type: github-advisory

## Affected
- PyPI: `transmute-core` — affected >=0 <1.13.5

## Details
Unsafe YAML deserialization in yaml.Loader in transmute-core before 1.13.5 allows attackers to execute arbitrary Python code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47204
- https://github.com/toumorokoshi/transmute-core/pull/58
- https://github.com/toumorokoshi/transmute-core/commit/29bf82eb8ed9926d31eec90aec482ecc0dcb23f0
- https://github.com/pypa/advisory-database/tree/main/vulns/transmute-core/PYSEC-2023-223.yaml
- https://github.com/toumorokoshi/transmute-core
- https://github.com/toumorokoshi/transmute-core/releases/tag/v1.13.5
