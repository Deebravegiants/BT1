# [M] DiskCache has unsafe pickle deserialization

## Summary
Severity: Medium
Advisory: GHSA-w8v5-vhqr-4h9v
CVE: CVE-2025-69872
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-w8v5-vhqr-4h9v
Type: github-advisory

## Affected
- PyPI: `diskcache` — affected >=0

## Details
DiskCache (python-diskcache) through 5.6.3 uses Python pickle for serialization by default. An attacker with write access to the cache directory can achieve arbitrary code execution when a victim application reads from the cache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69872
- https://github.com/EthanKim88/ethan-cve-disclosures/blob/main/CVE-2025-69872-DiskCache-Pickle-Deserialization.md
- https://github.com/grantjenks/python-diskcache
