# [H] PyTorch Lightning denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-98fp-7v67-4v3q
CVE: CVE-2024-8020
CWE: CWE-248
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-98fp-7v67-4v3q
Type: github-advisory

## Affected
- PyPI: `pytorch-lightning` — affected >=0

## Details
A vulnerability in lightning-ai/pytorch-lightning version 2.3.2 allows an attacker to cause a denial of service by sending an unexpected POST request to the `/api/v1/state` endpoint of `LightningApp`. This issue occurs due to improper handling of unexpected state values, which results in the server shutting down.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8020
- https://github.com/Lightning-AI/pytorch-lightning
- https://huntr.com/bounties/8b642a78-2b80-4fb0-9b2f-8ba0ff37db6a
