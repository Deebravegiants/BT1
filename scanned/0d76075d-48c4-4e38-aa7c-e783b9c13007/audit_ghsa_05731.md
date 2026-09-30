# [H] Azure Core is vulnerable to deserialization of untrusted data

## Summary
Severity: High
Advisory: GHSA-jm66-cg57-jjv5
CVE: CVE-2026-21226
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-jm66-cg57-jjv5
Type: github-advisory

## Affected
- PyPI: `azure-core` — affected >=0 <1.38.0

## Details
Deserialization of untrusted data in Azure Core shared client library for Python allows an authorized attacker to execute code over a network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-21226
- https://github.com/Azure/azure-sdk-for-python
- https://github.com/Azure/azure-sdk-for-python/blob/6d2e6431ea0991861640e449e51e894247a7771a/sdk/core/azure-core/CHANGELOG.md#1380-2026-01-12
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-21226
