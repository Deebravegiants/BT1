# [M] Apache NuttX RTOS: fs/inode: fs_inoderemove root inode removal

## Summary
Severity: Medium
Advisory: CVE-2025-48768
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-01
Source: https://osv.dev/vulnerability/CVE-2025-48768
Type: osv

## Details
Release of Invalid Pointer or Reference vulnerability was discovered in fs/inode/fs_inoderemove code of the Apache NuttX RTOS that allowed root filesystem inode removal leading to a debug assert trigger (that is disabled by default), NULL pointer dereference (handled differently depending on the target architecture), or in general, a Denial of Service.

This issue affects Apache NuttX RTOS: from 10.0.0 before 12.10.0.

Users of filesystem based services with write access that were exposed over the network (i.e. FTP) are affected and recommended to upgrade to version 12.10.0 that fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/12/31/10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48768.json
- https://lists.apache.org/thread/nwo1kd08b7t3dyz082q2pghdxwvxwyvo
- https://nvd.nist.gov/vuln/detail/CVE-2025-48768
- https://github.com/apache/nuttx/pull/16437
