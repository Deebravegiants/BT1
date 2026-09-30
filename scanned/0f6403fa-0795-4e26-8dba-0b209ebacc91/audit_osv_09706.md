# [H] CVE-2017-10971

## Summary
Severity: High
Advisory: CVE-2017-10971
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-06
Source: https://osv.dev/vulnerability/CVE-2017-10971
Type: osv

## Details
In the X.Org X server before 2017-06-19, a user authenticated to an X Session could crash or execute code in the context of the X Server by exploiting a stack overflow in the endianness conversion of X Events.

## References
- http://www.debian.org/security/2017/dsa-3905
- http://www.securityfocus.com/bid/99546
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=215f894965df5fb0bb45b107d84524e700d2073c
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=8caed4df36b1f802b4992edcfd282cbeeec35d9d
- https://cgit.freedesktop.org/xorg/xserver/commit/?id=ba336b24052122b136486961c82deac76bbde455
- https://bugzilla.suse.com/show_bug.cgi?id=1035283
