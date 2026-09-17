# [H] CVE-2017-13722

## Summary
Severity: High
Advisory: CVE-2017-13722
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-10-11
Source: https://osv.dev/vulnerability/CVE-2017-13722
Type: osv

## Details
In the pcfGetProperties function in bitmap/pcfread.c in libXfont through 1.5.2 and 2.x before 2.0.2, a missing boundary check (for PCF files) could be used by local attackers authenticated to an Xserver for a buffer over-read, for information disclosure or a crash of the X server.

## References
- http://www.debian.org/security/2017/dsa-3995
- https://security.gentoo.org/glsa/201711-08
- https://www.x.org/releases/individual/lib/libXfont2-2.0.2.tar.bz2
- https://bugzilla.redhat.com/show_bug.cgi?id=1500693
- https://bugzilla.suse.com/show_bug.cgi?id=1049692
- https://cgit.freedesktop.org/xorg/lib/libXfont/commit/?id=672bb944311392e2415b39c0d63b1e1902905bcd
