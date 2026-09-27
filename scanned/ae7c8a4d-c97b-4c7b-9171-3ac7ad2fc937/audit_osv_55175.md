# [M] CVE-2025-12801

## Summary
Severity: Medium
Advisory: CVE-2025-12801
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2025-12801
Type: osv

## Details
A vulnerability was recently discovered in the rpc.mountd daemon in the nfs-utils package for Linux, that allows a NFSv3 client to escalate the
privileges assigned to it in the /etc/exports file at mount time. In particular, it allows the client to access any subdirectory or subtree of an exported directory, regardless of the set file permissions, and regardless of any 'root_squash' or 'all_squash' attributes that would normally be expected to apply to that client.

## References
- https://access.redhat.com/errata/RHSA-2026:3940
- https://access.redhat.com/errata/RHSA-2026:3941
- https://access.redhat.com/errata/RHSA-2026:3942
- https://access.redhat.com/security/cve/CVE-2025-12801
- https://access.redhat.com/errata/RHSA-2026:3938
- https://access.redhat.com/errata/RHSA-2026:3939
- https://bugzilla.redhat.com/show_bug.cgi?id=2413081
