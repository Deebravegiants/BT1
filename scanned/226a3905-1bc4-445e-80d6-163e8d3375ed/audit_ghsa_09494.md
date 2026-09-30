# [C] stigmem-node: Auth-disabled deployments may grant broad anonymous access outside loopback

## Summary
Severity: Critical
Advisory: GHSA-fp6w-8wpg-74g5
CWE: CWE-285, CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-fp6w-8wpg-74g5
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a2

## Details
### Impact
Stigmem nodes configured with authentication disabled could grant the anonymous identity broad read/write/federation capabilities if exposed outside a loopback-only local development environment. Impacted users are operators who intentionally disabled authentication while binding the node to a non-loopback URL.

### Patches
Patched in 0.9.0a2. The node now refuses unauthenticated operation outside loopback-only local development.

### Workarounds
Before upgrading, keep authentication enabled for all non-local deployments and do not expose nodes with authentication disabled to untrusted networks.

### Upgrade
Upgrade to the patched release:

```bash
pip install --upgrade --pre stigmem-node
```

If developers install through the Stigmem meta-package instead, they should use the matching extra for their deployments, for example:

```bash
pip install --upgrade --pre 'stigmem[node]'
```

### Resources
- Release: https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a2
- Changelog: https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/CHANGELOG.md#L14-L35
- Security policy and posture: https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/SECURITY.md

## References
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-fp6w-8wpg-74g5
- https://github.com/eidetic-labs/stigmem
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/CHANGELOG.md#L14-L35
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/SECURITY.md
- https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a2
