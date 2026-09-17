# [M] Hatchet allows cross-tenant write/DoS to other tenants' workers via Dispatcher gRPC UpsertWorkerLabels and Unsubscribe

## Summary
Severity: Medium
Advisory: GHSA-8x7x-83cf-c3pg
CVE: CVE-2026-54746
CWE: CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-8x7x-83cf-c3pg
Type: github-advisory

## Affected
- Go: `github.com/hatchet-dev/hatchet` — affected >=0.40.0 <0.91.2

## Details
### Summary

A **cross-tenant write / DoS** vulnerability in the Hatchet `Dispatcher` gRPC service allows any holder of a normal tenant-scoped API token (the lowest credential Hatchet issues — an `OWNER` of a brand-new tenant) to overwrite the affinity labels of, or disconnect from the dispatcher, any worker UUID belonging to any other tenant on the same Hatchet instance. The two affected RPCs — `Dispatcher/UpsertWorkerLabels` and `Dispatcher/Unsubscribe` — read the caller's tenant from the bearer-token context only for analytics and response shaping, and never use it to authorise the `worker_id` from the request body.


### Impact
This CVE requires the attacker to successfully guess the target UUID. 
**Who is impacted.** Any Hatchet deployment that hosts more than one tenant on the same instance:
- **Hatchet Cloud (multi-tenant SaaS)** — every tenant is exposed to every other tenant.
- **Self-hosted Hatchet with multiple internal teams / business units sharing one instance** — each team is exposed to every other team on the box.
- **Any deployment where a single tenant's API token can be obtained by an attacker** (e.g. a leaked low-privilege CI token from a single tenant). One token is enough to attack every other tenant on the same instance.

Single-tenant self-hosted deployments are unaffected in practice (the "victim" and "attacker" tenants would be the same).

## References
- https://github.com/hatchet-dev/hatchet/security/advisories/GHSA-8x7x-83cf-c3pg
- https://github.com/hatchet-dev/hatchet/commit/591a30deb8b80f02eba7014997de387d710986c9
- https://github.com/hatchet-dev/hatchet
