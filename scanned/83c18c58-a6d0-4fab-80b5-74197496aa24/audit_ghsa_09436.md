# [C] stigmem-node's federation peer registration lacked explicit out-of-band approval

## Summary
Severity: Critical
Advisory: GHSA-9vp8-3hmv-8fgh
CWE: CWE-295, CWE-345
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-9vp8-3hmv-8fgh
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a2

## Details
### Impact
Federation peer registration accepted peer key material during registration without a separate administrator approval step based on an out-of-band fingerprint check. Impacted deployments are nodes that accept federation peer registration across a network where initial registration could be intercepted or misdirected.

### Patches
Patched in 0.9.0a2. Peer registration now uses a pending approval flow, and peer tokens are not accepted until an administrator approves the peer using the expected fingerprint.

### Workarounds
Before upgrading, restrict peer registration endpoints to trusted administrative networks and verify peer public-key fingerprints out of band before allowing federation traffic.

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
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-9vp8-3hmv-8fgh
- https://github.com/eidetic-labs/stigmem
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/CHANGELOG.md#L14-L35
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/SECURITY.md
- https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a2
