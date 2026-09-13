# [M] CVE-2020-14347

## Summary
Severity: Medium
Advisory: CVE-2020-14347
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-05
Source: https://osv.dev/vulnerability/CVE-2020-14347
Type: osv

## Details
A flaw was found in the way xserver memory was not properly initialized. This could leak parts of server memory to the X client. In cases where Xorg server runs with elevated privileges, this could result in possible ASLR bypass. Xorg-server before version 1.20.9 is vulnerable.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00075.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00066.html
- https://security.gentoo.org/glsa/202012-01
- https://www.openwall.com/lists/oss-security/2020/07/31/2
- https://usn.ubuntu.com/4488-1/
- https://usn.ubuntu.com/4488-2/
- https://www.debian.org/security/2020/dsa-4758
- https://lists.debian.org/debian-lts-announce/2020/08/msg00057.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14347
- https://lists.x.org/archives/xorg-announce/2020-July/003051.html
