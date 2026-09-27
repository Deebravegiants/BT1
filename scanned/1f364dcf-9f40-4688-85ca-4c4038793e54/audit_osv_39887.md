# [C] OpenReception: Tenant admin self-promotes to GLOBAL_ADMIN

## Summary
Severity: Critical
Advisory: CVE-2026-48086
Aliases: GHSA-5qfr-7q4g-3469
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48086
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. Prior to version 1.0.2, a TENANT_ADMIN promotes themselves to platform-wide GLOBAL_ADMIN through a single PUT request. The role-update handler accepts the `GLOBAL_ADMIN` enum value from any tenant admin updating their own tenant's staff. No policy check enforces that "only an existing GLOBAL_ADMIN may grant GLOBAL_ADMIN", so the schema validation IS the authorization decision. After re-login, the JWT contains the new role and the formerly-tenant-scoped admin reaches every other tenant on the platform. On the hosted OpenReception service this is a scope-changed escalation: a single customer-side tenant administrator gains full platform-wide administrative control over all other tenants' configuration, users, staff records, operational metadata, and tenant lifecycle. Plaintext appointment contents remain subject to the E2E model unless chained with the staff-crypto poisoning issue (V-4) or with staff-passkey hijacking (V-1). On a single-tenant self-hosted deployment it is still a privilege escalation because TENANT_ADMIN should not be able to create new tenants, modify global configuration, or manage other administrators. The same handler also accepts updates targeted at any colleague within the tenant. A tenant admin can promote a separate collaborator account instead of themselves, leaving their own audit trail clean while the platform-wide breach happens through a separate identity. Version 1.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48086.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-5qfr-7q4g-3469
- https://nvd.nist.gov/vuln/detail/CVE-2026-48086
- https://github.com/open-reception/appointment-booking-software/commit/8525d35a41c31078d9f01c62e9687e653cf1a494
