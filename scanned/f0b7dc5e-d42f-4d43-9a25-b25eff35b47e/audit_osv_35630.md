# [M] Missing Authorization in get_deployed_stack Endpoint in zenml-io/zenml

## Summary
Severity: Medium
Advisory: CVE-2026-11876
CVSS: 5.0 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-11876
Type: osv

## Details
In zenml-io/zenml version 0.94.2, the `GET /api/v1/stack-deployment/stack` endpoint (`get_deployed_stack`) lacks proper RBAC authorization checks, allowing any authenticated user to enumerate all deployed stacks across all users and tenants. This includes stack component details, service connector information, and user IDs of stack owners. The vulnerability arises from two issues: missing endpoint-level RBAC checks and the use of a server-side `Client()` that bypasses the RBAC enforcement layer by directly accessing the database through `SqlZenStore`. This exposes sensitive information such as infrastructure topology, service connector details, stack ownership, and deployment metadata, potentially enabling cross-tenant reconnaissance and further attacks in multi-tenant ZenML Pro/Cloud deployments.

## References
- https://huntr.com/bounties/3b434e02-0ee9-4b5e-a44b-0988b6f074c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11876.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11876
- https://github.com/zenml-io/zenml/commit/9ad2c65f24ded22a5a98d289d63a7f629b434b61
