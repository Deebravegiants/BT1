# [C] mamba language model framework vulnerable to insecure deserialization when loading pre-trained models from HuggingFace Hub

## Summary
Severity: Critical
Advisory: GHSA-pq2f-x424-6fjm
CVE: CVE-2026-31239
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-pq2f-x424-6fjm
Type: github-advisory

## Affected
- PyPI: `mamba-ssm` — affected >=0

## Details
The mamba language model framework thru 2.2.6 is vulnerable to insecure deserialization (CWE-502) when loading pre-trained models from HuggingFace Hub. The MambaLMHeadModel.from_pretrained() method uses torch.load() to load the pytorch_model.bin weight file without enabling the security-restrictive weights_only=True parameter. This allows the deserialization of arbitrary Python objects via the pickle module. An attacker can exploit this by publishing a malicious model repository on HuggingFace Hub. When a victim loads a model from this repository, arbitrary code is executed on the victim's system in the context of the mamba process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31239
- https://github.com/state-spaces/mamba
- https://www.notion.so/CVE-2026-31239-35d1e1393188810d9baedfbd8363f396
