# [M] CVE-2018-19364

## Summary
Severity: Medium
Advisory: CVE-2018-19364
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-13
Source: https://osv.dev/vulnerability/CVE-2018-19364
Type: osv

## Details
hw/9pfs/cofile.c and hw/9pfs/9p.c in QEMU can modify an fid path while it is being accessed by a second thread, leading to (for example) a use-after-free outcome.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CGCFIFSIWUREEQQOZDZFBYKWZHXCWBZN/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00023.html
- https://seclists.org/bugtraq/2019/May/76
- https://usn.ubuntu.com/3826-1/
- https://www.debian.org/security/2019/dsa-4454
- http://www.openwall.com/lists/oss-security/2018/11/20/1
- https://lists.gnu.org/archive/html/qemu-devel/2018-11/msg01139.html
- https://lists.gnu.org/archive/html/qemu-devel/2018-11/msg02795.html
