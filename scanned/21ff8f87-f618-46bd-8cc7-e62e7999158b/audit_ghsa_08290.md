# [H] PyTorch Lightning load_from_checkpoint has an insecure checkpoint deserialization

## Summary
Severity: High
Advisory: GHSA-75m9-98v2-hjpm
CVE: CVE-2026-31221
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-75m9-98v2-hjpm
Type: github-advisory

## Affected
- PyPI: `pytorch-lightning` — affected >=0

## Details
PyTorch-Lightning versions 2.6.0 and earlier contain an insecure deserialization vulnerability (CWE-502) in the checkpoint loading mechanism. The LightningModule.load_from_checkpoint() method, which is commonly used to load saved model states, internally calls torch.load() without setting the security-restrictive weights_only=True parameter. This default behavior allows the deserialization of arbitrary Python objects via the Pickle module. A remote attacker can exploit this by providing a maliciously crafted checkpoint file, leading to arbitrary code execution on the victim's system when the file is loaded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31221
- https://github.com/Lightning-AI/pytorch-lightning
- https://www.notion.so/CVE-2026-31221-35d1e1393188815f8db7c4fd08076639
