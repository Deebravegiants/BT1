# [H] stigmem-node's unsigned plugin override could be enabled without a second explicit acknowledgment

## Summary
Severity: High
Advisory: GHSA-w7pm-9g55-mxfm
CWE: CWE-494
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-w7pm-9g55-mxfm
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a2

## Details
### Impact
A single configuration flag could disable plugin signature enforcement. If an operator unintentionally carried that setting into an environment where plugin paths are writable by less-trusted users, unsigned plugin code could be loaded.

### Patches
Patched in 0.9.0a2. Disabling plugin signature enforcement now requires a second explicit acknowledgment value.

### Workarounds
Before upgrading, keep plugin signing required in all shared or production environments and ensure plugin directories are not writable by untrusted users.

### Upgrade
Upgrade to the patched release:

```bash
pip install --upgrade --pre stigmem-node
```

If developers install through the Stigmem meta-package instead, they should use the matching extra for deployments, for example:

```bash
pip install --upgrade --pre 'stigmem[node]'
```

### Resources
- Release: https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a2
- Changelog: https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/CHANGELOG.md#L14-L35
- Security policy and posture: https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/SECURITY.md

## References
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-w7pm-9g55-mxfm
- https://github.com/eidetic-labs/stigmem
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/CHANGELOG.md#L14-L35
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/SECURITY.md
- https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a2
