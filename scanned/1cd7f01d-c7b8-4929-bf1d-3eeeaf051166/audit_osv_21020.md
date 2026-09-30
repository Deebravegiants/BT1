# [M] CVE-2021-3975

## Summary
Severity: Medium
Advisory: CVE-2021-3975
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-3975
Type: osv

## Details
A use-after-free flaw was found in libvirt. The qemuMonitorUnregister() function in qemuProcessHandleMonitorEOF is called using multiple threads without being adequately protected by a monitor lock. This flaw could be triggered by the virConnectGetAllDomainStats API when the guest is shutting down. An unprivileged client with a read-only connection could use this flaw to perform a denial of service attack by causing the libvirt daemon to crash.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://security.netapp.com/advisory/ntap-20221201-0002/
- https://access.redhat.com/security/cve/CVE-2021-3975
- https://bugzilla.redhat.com/show_bug.cgi?id=2024326
- https://github.com/libvirt/libvirt/commit/1ac703a7d0789e46833f4013a3876c2e3af18ec7
- https://ubuntu.com/security/CVE-2021-3975
