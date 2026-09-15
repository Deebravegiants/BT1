# [M] Graphql: information disclosure via graphql introspection in openshift

## Summary
Severity: Medium
Advisory: CVE-2024-50312
Aliases: GO-2024-3211
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-10-22
Source: https://osv.dev/vulnerability/CVE-2024-50312
Type: osv

## Details
A vulnerability was found in GraphQL due to improper access controls on the GraphQL introspection query. This flaw allows unauthorized users to retrieve a comprehensive list of available queries and mutations. Exposure to this flaw increases the attack surface, as it can facilitate the discovery of flaws or errors specific to the application's GraphQL implementation.

## References
- https://catalog.redhat.com/software/containers/
- https://github.com/openshift/console/pull/14409/files
- https://access.redhat.com/errata/RHSA-2024:6122
- https://access.redhat.com/errata/RHSA-2025:0115
- https://access.redhat.com/errata/RHSA-2025:0140
- https://access.redhat.com/security/cve/CVE-2024-50312
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50312.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50312
- https://bugzilla.redhat.com/show_bug.cgi?id=2319378
