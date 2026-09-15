# [C] CVE-2017-12177

## Summary
Severity: Critical
Advisory: CVE-2017-12177
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2017-12177
Type: osv

## Details
xorg-x11-server before 1.19.5 was vulnerable to integer overflow in ProcDbeGetVisualInfo function allowing malicious X client to cause X server to crash or possibly execute arbitrary code.

## References
- https://lists.debian.org/debian-lts-announce/2017/11/msg00032.html
- https://security.gentoo.org/glsa/201711-05
- https://www.debian.org/security/2017/dsa-4000
- https://bugzilla.redhat.com/show_bug.cgi?id=1509218
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=4ca68b878e851e2136c234f40a25008297d8d831
