# [C] scio is vunerable to  Remote Command Execution  through PyTorch

## Summary
Severity: Critical
Advisory: GHSA-m9mp-6x32-5rhg
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-09
Source: https://github.com/advisories/GHSA-m9mp-6x32-5rhg
Type: github-advisory

## Affected
- PyPI: `scio-pypi` — affected >=0

## Details
### Impact
PyTorch reported a [**critical** vulnerability](https://github.com/pytorch/pytorch/security/advisories/GHSA-53q9-r3pm-6pq6) when using `torch.load`, even with option `weights_only=True`, for `torch <= 2.5.1`.

In `scio <= 1.0.0`, the lower bound for `torch` is `2.3`.

### Patches
The lower bound was changed to `torch >= 2.6`, starting from `scio >= 1.0.1` (currently in dev state).

### Workarounds
You can manually check that you are using `torch >= 2.6`.

## References
- https://github.com/ThalesGroup/scio/security/advisories/GHSA-m9mp-6x32-5rhg
- https://github.com/pytorch/pytorch/security/advisories/GHSA-53q9-r3pm-6pq6
- https://github.com/ThalesGroup/scio
