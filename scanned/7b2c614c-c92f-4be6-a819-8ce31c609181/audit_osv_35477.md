# [M] Foreman: satellite: graphql api permission bypass leads to information disclosure

## Summary
Severity: Medium
Advisory: CVE-2025-9572
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2025-9572
Type: osv

## Details
n authorization flaw in Foreman's GraphQL API allows low-privileged users to access metadata beyond their assigned permissions. Unlike the REST API, which correctly enforces access controls, the GraphQL endpoint does not apply proper filtering, leading to an authorization bypass.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://theforeman.org/security.html#2025-9572
- https://access.redhat.com/errata/RHSA-2025:21886
- https://access.redhat.com/errata/RHSA-2025:21893
- https://access.redhat.com/errata/RHSA-2025:21894
- https://access.redhat.com/errata/RHSA-2025:21897
- https://access.redhat.com/security/cve/CVE-2025-9572
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9572.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9572
- https://bugzilla.redhat.com/show_bug.cgi?id=2391715
- https://github.com/theforeman/foreman
