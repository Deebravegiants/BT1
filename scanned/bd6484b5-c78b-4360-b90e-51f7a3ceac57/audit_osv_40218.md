# [M] Foreman: foreman: information disclosure via improper validation of nested request parameters

## Summary
Severity: Medium
Advisory: CVE-2026-5138
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-5138
Type: osv

## Details
A flaw was found in Foreman. An authenticated user with host-edit permissions could exploit a cross-tenant information disclosure vulnerability. This flaw occurs because the taxonomy_scope controller method does not properly validate organization and location IDs from nested request parameters, bypassing existing authorization checks. This allows the user to leak sensitive infrastructure metadata, including subnet topology, IP ranges, gateways, DNS servers, and VLAN IDs, from organizations and locations they are not authorized to access.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:34365
- https://access.redhat.com/errata/RHSA-2026:34366
- https://access.redhat.com/errata/RHSA-2026:34367
- https://access.redhat.com/errata/RHSA-2026:34368
- https://access.redhat.com/security/cve/CVE-2026-5138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5138.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5138
- https://bugzilla.redhat.com/show_bug.cgi?id=2452971
