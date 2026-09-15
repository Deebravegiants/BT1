# [M] Iris has an Improper Authorization issue

## Summary
Severity: Medium
Advisory: CVE-2026-41522
Aliases: GHSA-3mxh-x92q-9r25
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-41522
Type: osv

## Details
Iris is a web collaborative platform that helps incident responders share technical details during investigations. Prior to version 2.4.28, DFIR-IRIS exposes an optional GraphQL endpoint at `/graphql` that does not enforce the same authorization checks as the REST API. Any authenticated user can abuse it in three ways: unauthorized IOC read across cases (IDOR), bulk IOC disclosure via `case.iocs`. The `case(caseId: …).iocs` resolver returns IOCs linked to an arbitrary case without verifying the caller has access to that case, and unauthorized case creation. All three are reachable by any authenticated user, regardless of role or case ACL. This is fixed in v2.4.28. The GraphQL blueprint, resolvers, and dependencies (`graphene`, `graphene-sqlalchemy`, `graphql-server[flask]`) were removed entirely, since the feature was not in use. As a workaround, block `/graphql` at the reverse proxy (recommended) or comment out the `graphql_blueprint` import and `register_blueprint` call in `source/app/views.py` and restart.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41522.json
- https://github.com/dfir-iris/iris-web/security/advisories/GHSA-3mxh-x92q-9r25
- https://nvd.nist.gov/vuln/detail/CVE-2026-41522
