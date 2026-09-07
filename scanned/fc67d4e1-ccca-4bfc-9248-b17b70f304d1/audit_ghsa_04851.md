# [H] stistigmem-node: quarantine review surface exposes and mutates other tenants' quarantined facts (cross-tenant BOLA)

## Summary
Severity: High
Advisory: GHSA-xhv3-q4xx-349r
CWE: CWE-639, CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-xhv3-q4xx-349r
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a12

## Details
### Summary
On a multi-tenant stigmem node, a tenant administrator could list, read, and **admit or reject** quarantined facts belonging to **other** tenants. The list/count queries and `_get_quarantined_fact` in `routes/quarantine.py` lacked an `f.tenant_id = identity.tenant_id` predicate, and the garden lookup was not tenant-scoped — reached via the `/v1/quarantine` list and admit/reject endpoints.

### Impact
Cross-tenant confidentiality (reading another tenant's quarantined content) and cross-tenant integrity (moderating — admitting or rejecting — another tenant's facts), gated only by a plain tenant `write` capability rather than a node-level admin authority.

### Affected configurations
This is a cross-**tenant** break. It is exploitable **only** on deployments running the opt-in `stigmem-plugin-multi-tenant` (multiple tenants on one node). A default single-tenant node has only `tenant="default"` — there is no second tenant to cross — so it is **not exploitable** on default deployments. The rating is HIGH for the multi-tenant deployments the plugin exists to isolate.

### Patches
Fixed in `0.9.0a12` (PR #728): `AND f.tenant_id = identity.tenant_id` was added to the list/count queries and `_get_quarantined_fact`; the garden lookup is now tenant-scoped; and any genuinely cross-tenant moderation is gated behind `can_admin_federation()` (node superadmin), not a tenant `write` capability. A tenant-B admin can no longer list, admit, or reject tenant-A's quarantined facts.

### Workarounds
None other than upgrading to `0.9.0a12`. Single-tenant deployments are unaffected.

## References
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-xhv3-q4xx-349r
- https://github.com/eidetic-labs/stigmem/pull/728
- https://github.com/eidetic-labs/stigmem
