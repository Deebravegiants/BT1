# [H] Allegro AI ClearML path traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-m95h-p4gg-wfw3
CVE: CVE-2024-24591
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-06
Source: https://github.com/advisories/GHSA-m95h-p4gg-wfw3
Type: github-advisory

## Affected
- PyPI: `clearml` — affected >=0.17.0

## Details
A path traversal vulnerability in versions 1.4.0 to 1.14.1 of the client SDK of Allegro AI’s ClearML platform enables a maliciously uploaded dataset to write local or remote files to an arbitrary location on an end user’s system when interacted with.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24591
- https://github.com/allegroai/clearml
- https://hiddenlayer.com/research/not-so-clear-how-mlops-solutions-can-muddy-the-waters-of-your-supply-chain
