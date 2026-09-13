# [M] Qemu: 9pfs: improper access control on special files

## Summary
Severity: Medium
Advisory: CVE-2023-2861
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-12-06
Source: https://osv.dev/vulnerability/CVE-2023-2861
Type: osv

## Details
A flaw was found in the 9p passthrough filesystem (9pfs) implementation in QEMU. The 9pfs server did not prohibit opening special files on the host side, potentially allowing a malicious client to escape from the exported 9p tree by creating and opening a device file in the shared folder.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00012.html
- https://access.redhat.com/security/cve/CVE-2023-2861
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2861.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2861
- https://security.netapp.com/advisory/ntap-20240125-0005/
- https://security.netapp.com/advisory/ntap-20240229-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2219266
- https://gitlab.com/qemu-project/qemu
