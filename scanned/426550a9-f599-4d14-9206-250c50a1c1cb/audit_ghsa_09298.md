# [M] Hatchet affected by cross-tenant information disclosure in `listTasksByDAGIds`

## Summary
Severity: Medium
Advisory: GHSA-55gc-6fmc-fpx9
CVE: CVE-2026-42572
CWE: CWE-639, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-55gc-6fmc-fpx9
Type: github-advisory

## Affected
- Go: `github.com/hatchet-dev/hatchet` — affected >=0 <0.83.39

## Details
## Summary

A missing authorization directive on the `GET /api/v1/stable/dags/tasks` endpoint caused Hatchet's tenant-membership check to be skipped for this route. A user authenticated to any tenant on the same Hatchet instance could query the endpoint with another tenant's UUID and a DAG UUID belonging to that tenant, and receive task metadata for that DAG.

This issue has been patched in **v0.83.39**. Hatchet Cloud has been patched and requires no action from users. Self-hosted users should upgrade.

## Impact

**Who is affected.** Multi-tenant Hatchet instances reachable by an attacker who can obtain an account on that instance. On Hatchet Cloud, account creation is open by default. On self-hosted instances, the API must be reachable by the attacker and the hostname known; instances deployed inside a VPC or with signup restricted are not exposed to arbitrary external actors.

**Prerequisites for exploitation.** An attacker needed:

1. An account on the target Hatchet instance.
2. The victim tenant's UUID.
3. At least one DAG UUID (`external_id`) belonging to that tenant.

The two UUIDs are not treated as secrets — they appear in URLs, API responses, audit logs, invitation flows, shared run links, and dashboard screenshots — but an attacker does need to learn them through some out-of-band channel before exploitation is possible.

**What could be disclosed.** For each child task of a targeted DAG, the endpoint returned:

- `display_name`, `action_id`, `step_id`
- `workflow_id`, `workflow_version_id`, `workflow_run_id`, `task_external_id`
- `tenant_id`, `retry_count`, `status`, timestamps
- `additional_metadata` (JSON)

The `additional_metadata` field is the most sensitive: Hatchet workflows commonly use it to carry domain context such as user identifiers, customer IDs, feature flags, or correlation tokens. Its contents vary by deployment.

**What was not disclosed.** The raw task `input` payload is not part of this endpoint's response shape and was not exposed through this issue. The scope is limited to task metadata, not task arguments or results.

**Exploitation status.** We have no evidence that this vulnerability was exploited prior to the patch.

## Root cause

Hatchet's multi-tenant authorization relies on an OpenAPI-driven middleware pipeline. Each authenticated operation declares `x-resources: ["tenant", ...]` in its spec. The `populator` middleware reads the declared resources, looks up the corresponding entities from request parameters, and stores them on the request context. The `authz` middleware then verifies that the authenticated user is a member of the tenant found on the context.

The `listTasksByDAGIds` operation accepted a `tenant` UUID as a query parameter, but its OpenAPI definition did not declare `x-resources: ["tenant"]`. As a result:

1. The populator, which early-returns when no resources are declared, did not populate the tenant onto the request context.
2. The authz middleware, which runs its membership check only when a tenant is present on the context, silently passed the request through.
3. The handler read the tenant UUID directly from the query parameter and used it as the filter in the downstream OLAP query.

The SQL query itself correctly filters by `tenant_id`, so it returned only rows matching the supplied UUID — but the UUID came from the caller rather than from an authorization-validated context, so the filter bounded the response to the *attacker-named* tenant rather than to a tenant the caller was authorized to read.

Every other authenticated operation in the same path file (`tasks.yaml`) correctly declared `x-resources`. This endpoint was the only authenticated operation in the file that did not.

## Patch

The fix adds the missing resource authz checks inline on the handler, enforcing valid tenant membership before the handler runs.

Shipped in **v0.83.39**.

## Remediation

**Hatchet Cloud.** No action required. The patch was deployed on April 23, 2026 within the same day it was reported.

**Self-hosted — recommended.** Upgrade to **v0.83.39** or later.

**Self-hosted — if you cannot upgrade immediately.** Either of the following reduces exposure until you can upgrade:

- Restrict account creation by setting `SERVER_AUTH_RESTRICTED_EMAIL_DOMAINS` to an allowlist of domains you control. This prevents arbitrary users from registering an account on your instance, which removes the most common path to the prerequisite account.
- Ensure the Hatchet API is not exposed to untrusted networks. We generally recommend running Hatchet inside a VPC and fronting the API with authenticated network controls; deployments configured this way were not reachable by arbitrary external attackers.

## Timeline

All times April 23, 2026.

- **14:05** — Reported to Hatchet.
- **16:28** — Patch deployed to Hatchet Cloud and released as v0.83.39.
- Public disclosure — this advisory.

## Credit

Reported by @sajdakabir.

Hatchet thanks the reporter for responsibly disclosing this issue and for the clear, reproducible writeup.

## References
- https://github.com/hatchet-dev/hatchet/security/advisories/GHSA-55gc-6fmc-fpx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42572
- https://github.com/hatchet-dev/hatchet
