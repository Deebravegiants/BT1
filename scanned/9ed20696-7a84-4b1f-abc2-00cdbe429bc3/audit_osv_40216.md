# [M] Foreman: foreman: unauthorized modification of host configurations via broken access control

## Summary
Severity: Medium
Advisory: CVE-2026-5135
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-5135
Type: osv

## Details
A flaw was found in Foreman. This broken access control vulnerability allows an authenticated user with host-edit permissions to retarget an existing lookup value override to a different host. This is achieved by modifying the match field through nested host attributes, effectively bypassing authorisation checks. The consequence is the potential for unauthorised modification of managed host configurations across different organisational and location boundaries.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:34365
- https://access.redhat.com/errata/RHSA-2026:34366
- https://access.redhat.com/errata/RHSA-2026:34367
- https://access.redhat.com/errata/RHSA-2026:34368
- https://access.redhat.com/security/cve/CVE-2026-5135
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5135.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5135
- https://bugzilla.redhat.com/show_bug.cgi?id=2452230
