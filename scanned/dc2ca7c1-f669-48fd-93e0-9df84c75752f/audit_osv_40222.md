# [M] Foreman: foreman: cross-tenant private ssh key disclosure via taxonomy scoping bypass

## Summary
Severity: Medium
Advisory: CVE-2026-5142
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-5142
Type: osv

## Details
A flaw was found in foreman. Authenticated users with 'view_keypairs' permission can bypass taxonomy scoping, allowing them to download private SSH (Secure Shell) keys from other organizations by directly querying key pair IDs. This vulnerability leads to cross-tenant data exposure in multi-tenant deployments, potentially compromising sensitive information.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:34365
- https://access.redhat.com/errata/RHSA-2026:34366
- https://access.redhat.com/errata/RHSA-2026:34367
- https://access.redhat.com/errata/RHSA-2026:34368
- https://access.redhat.com/security/cve/CVE-2026-5142
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5142.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5142
- https://bugzilla.redhat.com/show_bug.cgi?id=2452999
