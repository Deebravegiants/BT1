# [C] CWE-863: ABAC authorization bypass via trailing slash route normalization in Eclipse BaSyx Go Components

## Summary
Severity: Critical
Advisory: CVE-2026-15704
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-15704
Type: osv

## Details
In Eclipse BaSyx Go Components versions up to and including 1.0.0, ABAC-enabled deployments are vulnerable to an authorization bypass caused by inconsistent trailing-slash handling between the ABAC middleware and the HTTP router.



The shared router configuration used Chi's `middleware.StripSlashes`, so a request such as `GET /shells/` was dispatched to the registered `GET /shells` route. However, the ABAC middleware evaluated the original request path including the trailing slash. If ABAC route lookup did not find a matching slash-suffixed route, the request was passed onward and the router then stripped the slash and executed the protected handler without the intended ABAC authorization decision and without the expected ABAC query filters.



An unauthenticated or unauthorized network attacker could append a trailing slash to protected API routes to reach handlers that should have been denied by ABAC policy. Depending on the exposed component, HTTP method, and deployed policy, this could allow unauthorized read, create, update, delete, or upload operations.



The issue affects ABAC-enabled deployments of services that use the shared router and ABAC middleware, including AAS Repository, Submodel Repository, AAS Registry, Submodel Registry, Concept Description Repository, Discovery, AAS Environment upload, and related services. The issue is fixed in Eclipse BaSyx Go Components v1.0.1.

## References
- https://github.com/eclipse-basyx/basyx-go-components/releases/tag/v1.0.1
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/164
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/580
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15704.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15704
- https://github.com/eclipse-basyx/basyx-go-components/pull/442
