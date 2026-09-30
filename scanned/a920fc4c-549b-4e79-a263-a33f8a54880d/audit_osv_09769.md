# [M] CVE-2017-11434

## Summary
Severity: Medium
Advisory: CVE-2017-11434
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2017-11434
Type: osv

## Details
The dhcp_decode function in slirp/bootp.c in QEMU (aka Quick Emulator) allows local guest OS users to cause a denial of service (out-of-bounds read and QEMU process crash) via a crafted DHCP options string.

## References
- http://www.debian.org/security/2017/dsa-3925
- http://www.securityfocus.com/bid/99923
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://www.openwall.com/lists/oss-security/2017/07/19/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1472611
- https://lists.gnu.org/archive/html/qemu-devel/2017-07/msg05001.html
