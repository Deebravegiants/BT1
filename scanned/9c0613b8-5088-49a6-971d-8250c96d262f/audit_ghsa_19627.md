# [C] PyTorch Lightning path traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4cv3-v7pv-rfhf
CVE: CVE-2024-8019
CWE: CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-4cv3-v7pv-rfhf
Type: github-advisory

## Affected
- PyPI: `pytorch-lightning` — affected >=0 <2.4.0

## Details
In lightning-ai/pytorch-lightning version 2.3.2, a vulnerability exists in the `LightningApp` when running on a Windows host. The vulnerability occurs at the `/api/v1/upload_file/` endpoint, allowing an attacker to write or overwrite arbitrary files by providing a crafted filename. This can lead to potential remote code execution (RCE) by overwriting critical files or placing malicious files in sensitive locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8019
- https://github.com/lightning-ai/pytorch-lightning/commit/330af381de88cff17515418a341cbc1f9f127f9a
- https://github.com/pytorch/pytorch
- https://huntr.com/bounties/2754298b-5af5-48ef-8b38-999093ddf2bd
