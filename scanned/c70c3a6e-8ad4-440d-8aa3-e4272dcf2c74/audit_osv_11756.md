# [M] CVE-2017-9503

## Summary
Severity: Medium
Advisory: CVE-2017-9503
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2017-9503
Type: osv

## Details
QEMU (aka Quick Emulator), when built with MegaRAID SAS 8708EM2 Host Bus Adapter emulation support, allows local guest OS privileged users to cause a denial of service (NULL pointer dereference and QEMU process crash) via vectors involving megasas command processing.

## References
- http://www.securityfocus.com/bid/99010
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00020.html
- http://www.openwall.com/lists/oss-security/2017/06/08/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1459477
- https://lists.gnu.org/archive/html/qemu-devel/2017-06/msg01309.html
- https://lists.gnu.org/archive/html/qemu-devel/2017-06/msg01313.html
