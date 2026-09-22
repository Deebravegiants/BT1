# [H] nebula-mesh: Host advanced overrides allow YAML injection into agent config.yml

## Summary
Severity: High
Advisory: GHSA-7hp6-g3pq-3pc3
CVE: CVE-2026-47722
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-7hp6-g3pq-3pc3
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.2

## Details
`internal/configgen/generator.go:86,108,119` interpolates the operator-supplied `ListenHost` and `TunDevice` fields raw into a `text/template` that produces the agent's `config.yml`. `internal/web/advanced.go:20-35` accepts both with only `strings.TrimSpace` — no character or shape validation.

## Exploit
An operator (or attacker with any operator key, given the cross-tenant CRUD advisory) sets `adv_tun_device` to:

```
nebula0
lighthouse:
  am_lighthouse: true
  hosts: ["10.0.0.1"]
#
```

The agent fetches the rendered config on its next signed poll. On config reload, it loads the injected YAML keys: the host self-promotes to lighthouse, attracts mesh traffic, or sets `am_relay: true` to be selected as a relay. The `ListenHost` field has the same shape.

## Affected
All released versions prior to v0.3.2.

## Threat model
- **Today**: operator can compromise their own host's config (trivially allowed if they own the host, but they can also set lighthouse/relay flags that the operator-create form does NOT expose — privilege uplift within their own tenant).
- **Combined with the critical /api/v1 authz advisory**: any operator key can mutate ANOTHER tenant's host overrides and inject YAML there.
- **Post-fix of the authz advisory**: still relevant — the agent unconditionally trusts whatever config the server hands it, so any future operator-impersonation bug re-amplifies this.

## Suggested fix
Two options, either acceptable:

1. **Input validation** in `parseAdvancedFromForm` (`internal/web/advanced.go`):
   - `ListenHost`: regex `^[A-Za-z0-9.:\[\]_-]+$` (IPv4/IPv6/hostname)
   - `TunDevice`: regex `^[A-Za-z0-9_-]{1,15}$` (Linux IFNAMSIZ caps at 15)
   Reject invalid input with a form-level error; do not write to the host row.

2. **Safer marshalling**: switch `configgen/generator.go` to marshal a typed Go struct via `gopkg.in/yaml.v3` (which escapes correctly) instead of `text/template` string-concat. Larger change, but eliminates this entire injection class.

Option 2 is preferable long-term. Option 1 is the quick fix.

The `unsafe_routes` advanced field is already `netip.Parse{Prefix,Addr}`-validated at `enroll.go:226-233` — apply the same validation discipline to the other advanced fields.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-7hp6-g3pq-3pc3
- https://github.com/forgekeep/nebula-mesh/issues/126
- https://github.com/forgekeep/nebula-mesh/commit/c1506f7344ab375a145a7449b193af3f19bb41ef
- https://github.com/juev/nebula-mesh
