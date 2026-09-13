# [C] Axonflow fixed bugs by implementing multi-tenant isolation and access-control hardening

## Summary
Severity: Critical
Advisory: GHSA-9h64-2846-7x7f
CWE: CWE-200, CWE-208, CWE-770, CWE-862, CWE-863, CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-9h64-2846-7x7f
Type: github-advisory

## Affected
- Go: `github.com/getaxonflow/axonflow` — affected >=0 <7.5.0

## Details
## Summary

Eight independently-filed bug fixes in the v7.1.3 → v7.5.0 release window collectively close a set of multi-tenant isolation, access-control, and policy-enforcement defects in the AxonFlow platform. They are filed as a single consolidated advisory because the recommended remediation is a single platform upgrade.

## Affected versions

`< 7.5.0`. Specific items affect different earlier minors; see Impact below.

## Patched versions

`>= 7.5.0`.

## Impact

| # | Item | Affected | Patched | CWE |
|---|---|---|---|---|
| 1 | **MAP execution multi-tenant isolation.** A body-supplied `org_id` could override the Basic-auth-derived org for both execution recording and policy evaluation. In multi-tenant deployments with shared agents, this could record one tenant's request under another tenant's audit log and evaluate it under the wrong tenant's policy set. | `< 7.4.5` | `>= 7.4.5` | CWE-863 |
| 2 | **Cross-tenant audit-log leak via evidence/explain handlers.** The handlers behind `/api/v1/evidence/*` and `/api/v1/decisions/*/explain` failed open when the tenant context was missing, returning data scoped to a different tenant or returning data without scope. | `< 7.2.0` | `>= 7.2.0` | CWE-200, CWE-863 |
| 3 | **License-validation bypass on `onboard-customer`.** The portal customer-onboard endpoint lacked authentication and license-key validation, allowing unauthenticated callers to invoke the onboard flow. | `< 7.2.0` | `>= 7.2.0` | CWE-862 |
| 4 | **Tenant-scope fail-open on evidence/explain.** Distinct from item 2: when tenant headers were absent, the handler defaulted to a permissive read scope rather than refusing the request. | `< 7.2.0` | `>= 7.2.0` | CWE-862 |
| 5 | **Internal-service auth fallback bypass in non-Community modes.** Evaluation/Enterprise builds carried an auth fallback path that, under specific request shapes, could be exploited to bypass `apiAuthMiddleware`. | `< 7.2.0` | `>= 7.2.0` | CWE-863 |
| 6 | **Login timing / org-existence disclosure on the portal.** The login handler returned different timing and response bodies for invalid-org vs invalid-password, allowing org enumeration. | `< 7.1.3` | `>= 7.1.3` | CWE-208 |
| 7 | **Portal DoS via unbounded request body.** The portal accepted unbounded request bodies, allowing memory-exhaustion attacks. Capped at 1 MiB. | `< 7.1.5` | `>= 7.1.5` | CWE-770 |
| 8 | **SQL-injection enforcement regression on `try.getaxonflow.com`.** The Community SaaS hosted endpoint inherited the `warn` SQLi default introduced in v6.2.0, allowing SQL-injection-shaped requests to pass governance to the LLM. Self-hosted deployments were unaffected unless they manually changed the default. | `< 7.5.0` (try.getaxonflow.com only) | `>= 7.5.0` | CWE-89 |

## Remediation

Upgrade to AxonFlow platform **v7.5.0** or later. No configuration changes required — the platform is purely additive and existing API/SDK callers continue to work.

For users who can't upgrade immediately, item-specific mitigations:

- **Items 1–5:** ensure the agent middleware sets `X-Org-ID` / `X-Tenant-ID` from authenticated identity at the ingress, never accepting body-supplied identity.
- **Item 8 (Community SaaS):** `SQLI_ACTION=block` can be set explicitly via the agent task definition; v7.5.0 makes this the default.

## Resources

- AxonFlow v7.5.0 CHANGELOG entry: https://github.com/getaxonflow/axonflow/blob/main/CHANGELOG.md
- AxonFlow v7.5.0 GitHub Release: https://github.com/getaxonflow/axonflow/releases/tag/v7.5.0

## Credit

Identified by AxonFlow internal security review during the April 2026 quality-freeze epic.

## References
- https://github.com/getaxonflow/axonflow/security/advisories/GHSA-9h64-2846-7x7f
- https://github.com/getaxonflow/axonflow
- https://github.com/getaxonflow/axonflow/blob/main/CHANGELOG.md
- https://github.com/getaxonflow/axonflow/releases/tag/v7.5.0
