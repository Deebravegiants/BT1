# [H] Skops unsafe deserialization

## Summary
Severity: High
Advisory: GHSA-q49c-6v6g-wgq3
CVE: CVE-2024-37065
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-q49c-6v6g-wgq3
Type: github-advisory

## Affected
- PyPI: `skops` — affected >=0.6

## Details
Deserialization of untrusted data can occur in versions 0.6 or newer of the skops python library, enabling a maliciously crafted model to run arbitrary code on an end user's system when loaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37065
- https://hiddenlayer.com/sai-security-advisory/skops-june2024
- http://github.com/skops-dev/skops
