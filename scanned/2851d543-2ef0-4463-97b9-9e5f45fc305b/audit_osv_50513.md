# [M] CVE-2020-16293

## Summary
Severity: Medium
Advisory: CVE-2020-16293
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-16293
Type: osv

## Details
A null pointer dereference vulnerability in compose_group_nonknockout_nonblend_isolated_allmask_common() in base/gxblend.c of Artifex Software GhostScript v9.50 allows a remote attacker to cause a denial of service via a crafted PDF file. This is fixed in v9.51.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=7870f4951bcc6a153f317e3439e14d0e929fd231
- https://lists.debian.org/debian-lts-announce/2020/08/msg00032.html
- https://security.gentoo.org/glsa/202008-20
- https://usn.ubuntu.com/4469-1/
- https://www.debian.org/security/2020/dsa-4748
- https://bugs.ghostscript.com/show_bug.cgi?id=701795
