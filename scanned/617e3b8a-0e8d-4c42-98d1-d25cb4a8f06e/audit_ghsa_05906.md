# [M] Graylog Server: System Catalog titles endpoint can be used to retrieve values of protected database fields

## Summary
Severity: Medium
Advisory: GHSA-q79r-r9xg-r863
CVE: CVE-2026-55425
CWE: CWE-213
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-q79r-r9xg-r863
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=7.1.0 <7.1.4

## Details
### Impact

A vulnerability was found in Graylog's API endpoint for retrieving system catalog entity titles. Authenticated users could retrieve database fields of supported entities by sending a custom API request. These fields can include e.g. the password hash of a user (but not the password itself), which should not be returned through the API, regardless of the endpoint. Permission checks do still apply, so users can retrieve their own password hash, but not those of other users. The admin user (or any user with an admin role) can retrieve password hashes of all users.

### Patches

This issue has been patched in Graylog `7.1.4`. In this version, an allow list will be used to check if protected fields are being accessed, refusing those requests. Affected users should upgrade to `7.1.4` or above to remediate the vulnerability.

### Workarounds

There is no known workaround. Upgrading to a patched version is recommended.

### Credits

Thanks to [Evelynkaz](https://github.com/Evelynkaz) for reporting.

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-q79r-r9xg-r863
- https://github.com/Graylog2/graylog2-server/pull/26284
- https://github.com/Graylog2/graylog2-server/commit/1d1a91d99c3d2d8993e61c3c52344648163d3a21
- https://github.com/Graylog2/graylog2-server/commit/da7767a44233b6a683d0713eed08da31ce0e77b5
- https://github.com/Graylog2/graylog2-server
- https://github.com/Graylog2/graylog2-server/releases/tag/7.1.4
- https://github.com/Graylog2/graylog2-server/releases/tag/7.2.0-alpha.2
