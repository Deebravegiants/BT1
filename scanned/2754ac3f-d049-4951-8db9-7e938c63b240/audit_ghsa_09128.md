# [H] flash-attention contains an insecure deserialization vulnerability in its checkpoint loading mechanism

## Summary
Severity: High
Advisory: GHSA-7g5w-pq96-8c5w
CVE: CVE-2026-31253
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-7g5w-pq96-8c5w
Type: github-advisory

## Affected
- PyPI: `flash_attn` — affected >=0

## Details
The flash-attention training framework thru commit e724e2588cbe754beb97cf7c011b5e7e34119e62 (2025-13-04) contains an insecure deserialization vulnerability (CWE-502) in its checkpoint loading mechanism. The load_checkpoint() function in checkpoint.py and the checkpoint loading code in eval.py use torch.load() without enabling the security-restrictive weights_only=True parameter. This allows the deserialization of arbitrary Python objects via the pickle module. An attacker can exploit this by providing a maliciously crafted checkpoint file. When a victim loads this checkpoint during model warmstarting or evaluation, arbitrary code is executed on the victim's system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31253
- https://github.com/Dao-AILab/flash-attention
- https://www.notion.so/CVE-2026-31253-35d1e1393188813f9e77e2038104bc49
