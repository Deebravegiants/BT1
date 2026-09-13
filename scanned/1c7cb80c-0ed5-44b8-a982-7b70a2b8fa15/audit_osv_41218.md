# [H] JeecgBoot 3.9.2 - Missing Authorization on OpenAPI Credential Management Endpoints Exposes Access/Secret Keys

## Summary
Severity: High
Advisory: CVE-2026-58377
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58377
Type: osv

## Details
JeecgBoot through 3.9.2 contains a broken access control vulnerability that allows authenticated low-privilege users to perform full create, read, update, and delete operations on OpenAPI credentials by accessing the OpenApiAuthController and OpenApiPermissionController endpoints which lack Shiro authorization annotations. Attackers can exploit the unenforced access controls to list, add, edit, and delete all AK/SK credential pairs, with the list endpoint returning secret keys in plaintext, enabling credential theft and unauthorized invocation of the OpenAPI surface.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58377.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58377
- https://www.vulncheck.com/advisories/jeecgboot-missing-authorization-on-openapi-credential-management-endpoints-exposes-access-secret-keys
- https://github.com/jeecgboot/JeecgBoot
- https://github.com/jeecgboot/JeecgBoot/issues/9705
