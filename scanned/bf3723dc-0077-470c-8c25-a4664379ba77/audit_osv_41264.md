# [C] PyTorch Lightning Arbitrary Code Execution via _instantiator Hyperparameter

## Summary
Severity: Critical
Advisory: CVE-2026-58659
Aliases: GHSA-qqmf-gpg7-g8gw, PYSEC-2026-3624, PYSEC-2026-3967
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-58659
Type: osv

## Details
PyTorch Lightning through 2.6.5, fixed in commit d710d68, contains a remote code execution vulnerability in the _load_state function that imports and executes attacker-controlled module names from checkpoint _instantiator hyperparameters. Attackers can craft malicious checkpoint files that bypass weights_only=True protections to execute arbitrary code when LightningModule.load_from_checkpoint is called.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58659.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58659
- https://www.vulncheck.com/advisories/pytorch-lightning-arbitrary-code-execution-via-instantiator-hyperparameter
- https://github.com/Lightning-AI/pytorch-lightning/pull/21832
- https://github.com/Lightning-AI/pytorch-lightning/commit/d710d689510d50e800f53b3cd773cbca20b1f86f
- https://github.com/Lightning-AI/pytorch-lightning
- https://github.com/Lightning-AI/pytorch-lightning/issues/21822
