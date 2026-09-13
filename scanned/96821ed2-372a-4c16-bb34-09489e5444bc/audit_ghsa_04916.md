# [H] stigmem-node: decay sweep expires and counts facts across all tenants (cross-tenant BOLA)

## Summary
Severity: High
Advisory: GHSA-6gqw-jqv7-v88m
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-6gqw-jqv7-v88m
Type: github-advisory

## Affected
- PyPI: `stigmem-node` — affected >=0 <0.9.0a12

## Details
### Summary
On a multi-tenant stigmem node, a caller holding a `write` credential for **one** tenant can run a decay sweep that acts on **every** tenant's facts. The candidate-selection queries in `lifecycle/decay.py` (`_select_ttl_candidates`, `_select_confidence_candidates`) carried no `tenant_id` predicate, and the caller's tenant was not threaded into the sweep or its async worker (`run_decay_sweep` / `_decay_job_worker`), reached via `POST /v1/decay/sweep`.

### Impact
A sweep with `ttl_seconds=0` expires **all tenants'** facts — cross-tenant data destruction (integrity and availability). A `dry_run` sweep returns a global candidate count, acting as a cross-tenant existence/volume **oracle** (information disclosure).

### Affected configurations
This is a cross-**tenant** break. It is exploitable **only** on deployments running the opt-in `stigmem-plugin-multi-tenant` (multiple tenants on one node). A default single-tenant node has only `tenant="default"` — there is no second tenant to cross — so it is **not exploitable** on default deployments. The rating is HIGH for the multi-tenant deployments the plugin exists to isolate.

### Patches
Fixed in `0.9.0a12` (PR #728): `identity.tenant_id` is threaded into `run_decay_sweep` and `_decay_job_worker`, and `AND tenant_id = ?` was added to the candidate selectors and the graph-sync. A tenant-B sweep now leaves tenant-A facts untouched, and `dry_run` counts only the caller's tenant. The `check_fact_query_tenant_scope.py` CI guard was extended to scan `lifecycle/` so this class cannot silently regress.

### Workarounds
None other than upgrading to `0.9.0a12`. Single-tenant deployments are unaffected.

## References
- https://github.com/eidetic-labs/stigmem/security/advisories/GHSA-6gqw-jqv7-v88m
- https://github.com/eidetic-labs/stigmem/pull/728
- https://github.com/eidetic-labs/stigmem
