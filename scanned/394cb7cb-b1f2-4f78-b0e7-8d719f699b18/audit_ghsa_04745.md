# [H] stigmem-node: RTBF tombstones are mis-attributed and suppress reads tenant-blind (cross-tenant BOLA)

## Summary
Severity: High
Advisory: GHSA-x26h-xmv8-gxf7
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-x26h-xmv8-gxf7
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a12

## Details
### Summary
On a multi-tenant stigmem node, RTBF (right-to-be-forgotten) tombstones were mis-scoped two ways. (1) `issue_tombstone` defaulted the tenant to `"default"` instead of the caller's tenant, so tombstones could be written to the wrong tenant. (2) The read-suppression path — `_get_tombstone_filter` (`routes/facts/common.py`) and the `_tombstone_scope_cache` (`lifecycle/tombstones.py`) — had no `tenant_id` predicate, so tombstone suppression was applied tenant-blind across fact queries and provenance. Reached via `/v1/tombstones` and the fact query/provenance read paths.

### Impact
Cross-tenant integrity of the RTBF mechanism: a tenant's deletion request could be recorded against the wrong tenant, and tombstone suppression could hide — or fail to hide — facts across tenant boundaries, undermining both data-view correctness and RTBF guarantees.

### Affected configurations
This is a cross-**tenant** break. It is exploitable **only** on deployments running the opt-in `stigmem-plugin-multi-tenant` (multiple tenants on one node). A default single-tenant node has only `tenant="default"` — there is no second tenant to cross — so it is **not exploitable** on default deployments. The rating is HIGH for the multi-tenant deployments the plugin exists to isolate.

### Patches
Fixed in `0.9.0a12` (PR #728): `identity.tenant_id` is passed from `issue_tombstone` into `create_tombstone` (no more `"default"` fallback); `AND tenant_id = ?` was added to `_get_tombstone_filter` and `get_tombstone_status`; the suppression cache is re-keyed to include tenant; and all four read call sites thread the caller's tenant. A tenant-B tombstone now suppresses only tenant-B facts and is invisible to tenant-A reads.

### Workarounds
None other than upgrading to `0.9.0a12`. Single-tenant deployments are unaffected.

## References
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-x26h-xmv8-gxf7
- https://github.com/eidetic-labs/stigmem/pull/728
- https://github.com/eidetic-labs/stigmem
