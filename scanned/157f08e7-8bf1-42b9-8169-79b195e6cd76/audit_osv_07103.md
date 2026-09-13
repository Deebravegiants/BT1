# [H] Apache NiFi: Missing Authorization of Restricted Permissions when Replacing Flow Contents

## Summary
Severity: High
Advisory: BIT-nifi-2026-44914
Aliases: CVE-2026-44914, GHSA-r2g5-993q-664g
Ecosystem: Bitnami
Published: 2026-06-24
Source: https://osv.dev/vulnerability/BIT-nifi-2026-44914
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.12.0 <2.10.0

## Details
Apache NiFi 1.12.0 through 2.9.0 are missing authorization when replacing Process Groups that include extension components with specific Required Permissions based on the Restricted annotation. The Restricted annotation indicates additional privileges required, but framework authorization did not check restricted status when handling requests to replace Process Groups. The missing authorization permits a user with general write access to add components with Restricted status. Apache NiFi installations that do not implement specific authorization for Restricted components are not subject to this vulnerability because the framework enforces write permissions as the security boundary. Upgrading to Apache NiFi 2.9.0 is the recommended mitigation, which removes the implementation of Restricted status authorization from the framework.

## References
- http://www.openwall.com/lists/oss-security/2026/06/20/6
- https://lists.apache.org/thread/ydr34t03xd1n0t9oogpzogjrd5y93838
- https://nvd.nist.gov/vuln/detail/CVE-2026-44914
