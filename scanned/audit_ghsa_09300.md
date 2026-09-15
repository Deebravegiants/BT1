# [H] stigmem-node's Postgres schema identifier handling required defensive quoting

## Summary
Severity: High
Advisory: GHSA-9pc9-4crj-mhpj
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-9pc9-4crj-mhpj
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a2

## Details
### Impact
Postgres backend schema identifiers were interpolated into SQL strings. In the reviewed code path the schema value is operator-controlled, but the pattern was unsafe if future call sites allowed tenant or request-controlled schema names. Impacted users are operators using the Postgres backend in affected versions.

### Patches
Patched in 0.9.0a2. Schema identifier handling now uses defensive identifier quoting and validation-oriented regression coverage.

### Workarounds
Before upgrading, only configure Postgres schema names from trusted deployment configuration and do not derive schema names from request, tenant, header, or user input.

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
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-9pc9-4crj-mhpj
- https://github.com/eidetic-labs/stigmem
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/CHANGELOG.md#L14-L35
- https://github.com/eidetic-labs/stigmem/blob/v0.9.0a2/SECURITY.md
- https://github.com/eidetic-labs/stigmem/releases/tag/v0.9.0a2
