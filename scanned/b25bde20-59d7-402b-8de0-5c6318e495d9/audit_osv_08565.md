# [M] CVE-2016-4429

## Summary
Severity: Medium
Advisory: CVE-2016-4429
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-10
Source: https://osv.dev/vulnerability/CVE-2016-4429
Type: osv

## Details
Stack-based buffer overflow in the clntudp_call function in sunrpc/clnt_udp.c in the GNU C Library (aka glibc or libc6) allows remote servers to cause a denial of service (crash) or possibly unspecified other impact via a flood of crafted ICMP and UDP packets.

## References
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- https://lists.debian.org/debian-lts-announce/2020/06/msg00027.html
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=bc779a1a5b3035133024b21e2f339fe4219fb11c
- https://www.oracle.com//security-alerts/cpujul2021.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00030.html
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00039.html
- http://www.securityfocus.com/bid/102073
- https://source.android.com/security/bulletin/2017-12-01
- https://usn.ubuntu.com/3759-1/
- https://usn.ubuntu.com/3759-2/
- https://sourceware.org/bugzilla/show_bug.cgi?id=20112
