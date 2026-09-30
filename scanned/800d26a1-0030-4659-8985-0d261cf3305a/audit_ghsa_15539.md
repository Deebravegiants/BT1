# [H] Cleanlab Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-8cm9-rrgc-4pcj
CVE: CVE-2024-45857
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-12
Source: https://github.com/advisories/GHSA-8cm9-rrgc-4pcj
Type: github-advisory

## Affected
- PyPI: `cleanlab` — affected >=2.4.0

## Details
Deserialization of untrusted data can occur in versions 2.4.0 or newer of the Cleanlab project, enabling a maliciously crafted datalab.pkl file to run arbitrary code on an end user’s system when the data directory is loaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45857
- https://github.com/cleanlab/cleanlab
- https://github.com/cleanlab/cleanlab/blob/v2.6.6/cleanlab/datalab/internal/serialize.py#L102-L138
- https://hiddenlayer.com/sai-security-advisory/2024-09-cleanlab
