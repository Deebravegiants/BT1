# [H] stigmem-node's federation peer token timestamp validation may reject valid peer tokens

## Summary
Severity: High
Advisory: GHSA-xh5j-xjfq-qvvx
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-xh5j-xjfq-qvvx
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a2

## Details
### Impact
A mismatch in federation peer-token timestamp handling could cause valid peer tokens to be treated as expired. Impacted deployments are Stigmem nodes using federation peer authentication paths from affected versions. The primary impact is availability and reliability of authenticated federation flows.

### Patches
Patched in 0.9.0a2. Federation peer-token timestamp handling now uses the canonical millisecond-based validation path and is covered by regression tests.

### Workarounds
Before upgrading, avoid mixed peer-token minting paths and restrict federation use to tightly controlled peers.

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
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-xh5j-xjfq-qvvx
- https://github.com/eidetic-labs/stigmem
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/CHANGELOG.md#L14-L35
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/SECURITY.md
- https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a2
