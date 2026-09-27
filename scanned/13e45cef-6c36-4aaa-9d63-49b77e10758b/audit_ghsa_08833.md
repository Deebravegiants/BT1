# [C] stigmem-node's federation insecure transport settings may allow non-loopback cleartext federation

## Summary
Severity: Critical
Advisory: GHSA-jmfc-hfjq-pxcp
CWE: CWE-319, CWE-489
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-jmfc-hfjq-pxcp
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a2

## Details
### Impact
Stigmem nodes with federation enabled could be configured to run without mTLS outside loopback-only local development. In affected deployments, federation traffic may traverse the network without the intended transport protection. Impacted users are operators who enabled federation and explicitly disabled mTLS while binding the node to a non-loopback URL.

### Patches
Patched in 0.9.0a2. The node now refuses this configuration unless insecure federation is limited to loopback-only local development.

### Workarounds
Before upgrading, operators should enable mTLS for federation or ensure federation endpoints are bound only to loopback/private test environments and are not reachable by untrusted networks.

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
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-jmfc-hfjq-pxcp
- https://github.com/eidetic-labs/stigmem
