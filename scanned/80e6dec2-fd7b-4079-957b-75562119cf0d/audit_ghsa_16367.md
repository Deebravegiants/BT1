# [H] Allegro AI ClearML vulnerable to deserialization of untrusted data

## Summary
Severity: High
Advisory: GHSA-cpcw-9h9m-wqw9
CVE: CVE-2024-24590
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-06
Source: https://github.com/advisories/GHSA-cpcw-9h9m-wqw9
Type: github-advisory

## Affected
- PyPI: `clearml` — affected >=0.17.0

## Details
Deserialization of untrusted data can occur in versions 0.17.0 to 1.14.2 of the client SDK of Allegro AI’s ClearML platform, enabling a maliciously uploaded artifact to run arbitrary code on an end user’s system when interacted with.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24590
- https://github.com/allegroai/clearml
- https://hiddenlayer.com/research/not-so-clear-how-mlops-solutions-can-muddy-the-waters-of-your-supply-chain
