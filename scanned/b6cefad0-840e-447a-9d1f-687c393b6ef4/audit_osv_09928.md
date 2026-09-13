# [C] CVE-2017-12179

## Summary
Severity: Critical
Advisory: CVE-2017-12179
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2017-12179
Type: osv

## Details
xorg-x11-server before 1.19.5 was vulnerable to integer overflow in (S)ProcXIBarrierReleasePointer functions allowing malicious X client to cause X server to crash or possibly execute arbitrary code.

## References
- https://security.gentoo.org/glsa/201711-05
- https://www.debian.org/security/2017/dsa-4000
- https://bugzilla.redhat.com/show_bug.cgi?id=1509220
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=d088e3c1286b548a58e62afdc70bb40981cdb9e8
