# [C] Airbyte Platform through 2.0.0 Cross-Workspace Authorization Bypass via Caller-Supplied workspaceId

## Summary
Severity: Critical
Advisory: CVE-2026-80049
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80049
Type: osv

## Details
Airbyte Platform resolves the workspace used for its authorization decision from a field the caller supplies. AuthorizationServerHandler copies recognised identifiers out of the raw JSON request body into X-Airbyte-* headers, and AuthenticationHeaderResolver.resolveWorkspace consults X-Airbyte-Workspace-Id ahead of every resource-derived header, including those for connection, source and destination identifiers. Endpoints whose declared request bodies carry only a resource identifier are nonetheless reached with an added workspaceId field, because the extractor reads the body rather than the endpoint's schema, so the permission check is performed against the workspace the caller nominated while the handler acts on the resource identifier the caller supplied. Nothing afterwards compares the resource's owning workspace with the one that was authorized. A member of any workspace can therefore read source and destination configuration, trigger and cancel syncs, and delete connections, sources and destinations that belong to workspaces they have no access to, at whatever privilege level their own workspace membership grants them.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80049.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80049
- https://www.vulncheck.com/advisories/airbyte-platform-through-2.0.0-cross-workspace-authorization-bypass-via-caller-supplied-workspaceid
- https://github.com/airbytehq/airbyte-platform
- https://github.com/airbytehq/airbyte-platform/blob/v2.0.0/airbyte-commons-server/src/main/kotlin/io/airbyte/commons/server/support/AuthenticationHeaderResolver.kt
- https://github.com/geo-chen/oss/blob/main/airbyte-platform.md
