# [M] CVE-2021-3607

## Summary
Severity: Medium
Advisory: CVE-2021-3607
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2021-3607
Type: osv

## Details
An integer overflow was found in the QEMU implementation of VMWare's paravirtual RDMA device in versions prior to 6.1.0. The issue occurs while handling a "PVRDMA_REG_DSRHIGH" write from the guest due to improper input validation. This flaw allows a privileged guest user to make QEMU allocate a large amount of memory, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.gentoo.org/glsa/202208-27
- https://security.netapp.com/advisory/ntap-20220318-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=1973349
- https://lists.gnu.org/archive/html/qemu-devel/2021-06/msg07925.html
