# [M] CVE-2021-3582

## Summary
Severity: Medium
Advisory: CVE-2021-3582
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-3582
Type: osv

## Details
A flaw was found in the QEMU implementation of VMWare's paravirtual RDMA device. The issue occurs while handling a "PVRDMA_CMD_CREATE_MR" command due to improper memory remapping (mremap). This flaw allows a malicious guest to crash the QEMU process on the host. The highest threat from this vulnerability is to system availability.

## References
- https://security.netapp.com/advisory/ntap-20220429-0003/
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://bugzilla.redhat.com/show_bug.cgi?id=1966266
