# [H] selinux: fix overlayfs mmap() and mprotect() access checks

## Summary
Severity: High
Advisory: CVE-2026-46054
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46054
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

selinux: fix overlayfs mmap() and mprotect() access checks

The existing SELinux security model for overlayfs is to allow access if
the current task is able to access the top level file (the "user" file)
and the mounter's credentials are sufficient to access the lower
level file (the "backing" file).  Unfortunately, the current code does
not properly enforce these access controls for both mmap() and mprotect()
operations on overlayfs filesystems.

This patch makes use of the newly created security_mmap_backing_file()
LSM hook to provide the missing backing file enforcement for mmap()
operations, and leverages the backing file API and new LSM blob to
provide the necessary information to properly enforce the mprotect()
access controls.

## References
- https://git.kernel.org/stable/c/82544d36b1729153c8aeb179e84750f0c085d3b1
- https://git.kernel.org/stable/c/8bacd09f12c27710228562e4d13163e58c5f4a45
- https://git.kernel.org/stable/c/bc6c380c1159de52a252ed11f19a42c47f60a735
- https://git.kernel.org/stable/c/cd0e707a927a70cdfd8bc5a512a9719a87f5ed51
- https://git.kernel.org/stable/c/d844702198395d3f80222777030f69db6be6b709
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46054.json
- https://access.redhat.com/errata/RHSA-2026:25191
- https://access.redhat.com/errata/RHSA-2026:27811
- https://access.redhat.com/errata/RHSA-2026:27812
- https://access.redhat.com/errata/RHSA-2026:30848
- https://access.redhat.com/errata/RHSA-2026:51746
- https://access.redhat.com/errata/RHSA-2026:52649
- https://access.redhat.com/errata/RHSA-2026:52667
- https://access.redhat.com/errata/RHSA-2026:52764
- https://access.redhat.com/errata/RHSA-2026:59091
- https://access.redhat.com/errata/RHSA-2026:59473
- https://access.redhat.com/security/cve/CVE-2026-46054
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46054.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46054
- https://bugzilla.redhat.com/show_bug.cgi?id=2482025
