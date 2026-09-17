# [M] Samba: smb clients can truncate files with read-only permissions

## Summary
Severity: Medium
Advisory: CVE-2023-4091
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-4091
Type: osv

## Details
A vulnerability was discovered in Samba, where the flaw allows SMB clients to truncate files, even with read-only permissions when the Samba VFS module "acl_xattr" is configured with "acl_xattr:ignore system acls = yes". The SMB protocol allows opening files when the client requests read-only access but then implicitly truncates the opened file to 0 bytes if the client specifies a separate OVERWRITE create disposition request. The issue arises in configurations that bypass kernel file system permissions checks, relying solely on Samba's permissions.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/04/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZUMVALLFFDFC53JZMUWA6HPD7HUGAP5I/
- https://www.samba.org/samba/security/CVE-2023-4091.html
- https://access.redhat.com/errata/RHSA-2023:6209
- https://access.redhat.com/errata/RHSA-2023:6744
- https://access.redhat.com/errata/RHSA-2023:7371
- https://access.redhat.com/errata/RHSA-2023:7408
- https://access.redhat.com/errata/RHSA-2023:7464
- https://access.redhat.com/errata/RHSA-2023:7467
- https://access.redhat.com/security/cve/CVE-2023-4091
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4091.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4091
- https://security.netapp.com/advisory/ntap-20231124-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2241882
- https://bugzilla.samba.org/show_bug.cgi?id=15439
