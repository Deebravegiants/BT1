# [H] CVE-2021-27365

## Summary
Severity: High
Advisory: CVE-2021-27365
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-07
Source: https://osv.dev/vulnerability/CVE-2021-27365
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.3. Certain iSCSI data structures do not have appropriate length constraints or checks, and can exceed the PAGE_SIZE value. An unprivileged user can send a Netlink message that is associated with iSCSI, and has a length up to the maximum length of a Netlink message.

## References
- http://packetstormsecurity.com/files/162117/Kernel-Live-Patch-Security-Notice-LSN-0075-1.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- https://security.netapp.com/advisory/ntap-20210409-0001/
- https://www.openwall.com/lists/oss-security/2021/03/06/1
- https://bugzilla.suse.com/show_bug.cgi?id=1182715
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f9dbdf97a5bd92b1a49cee3d591b55b11fd7a6d5
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ec98ea7070e94cc25a422ec97d1421e28d97b7ee
- https://blog.grimm-co.com/2021/03/new-old-bugs-in-linux-kernel.html
