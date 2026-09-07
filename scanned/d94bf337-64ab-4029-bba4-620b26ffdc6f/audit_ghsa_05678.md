# [H] PyTorch Vulnerable to Remote Code Execution via Untrusted Checkpoint Files

## Summary
Severity: High
Advisory: GHSA-63cw-57p8-fm3p
CVE: CVE-2026-24747
CWE: CWE-502, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-63cw-57p8-fm3p
Type: github-advisory

## Affected
- PyPI: `pytorch` — affected >=0 <2.10.0

## Details
### Summary

A vulnerability in PyTorch's `weights_only` unpickler allows an attacker to craft a malicious checkpoint file (`.pth`) that, when loaded with `torch.load(..., weights_only=True)`, can corrupt memory and potentially lead to arbitrary code execution.

### Vulnerability Details

The `weights_only=True` unpickler failed to properly validate pickle opcodes and storage metadata, allowing:

1. **Heap memory corruption** via `SETITEM`/`SETITEMS` opcodes applied to non-dictionary types
2. **Storage size mismatch** between declared element count and actual data in the archive

### Impact

An attacker who can convince a user to load a malicious checkpoint file may achieve arbitrary code execution in the context of the victim's process.


# Credit
Ji'an Zhou

## References
- https://github.com/pytorch/pytorch/security/advisories/GHSA-63cw-57p8-fm3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-24747
- https://github.com/pytorch/pytorch/issues/163105
- https://github.com/pytorch/pytorch
- https://github.com/pytorch/pytorch/163122/commit/954dc5183ee9205cbe79876ad05dd2d9ae752139
- https://github.com/pytorch/pytorch/releases/tag/v2.10.0
