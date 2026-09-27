# [H] CVE-2018-14424

## Summary
Severity: High
Advisory: CVE-2018-14424
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-14
Source: https://osv.dev/vulnerability/CVE-2018-14424
Type: osv

## Details
The daemon in GDM through 3.29.1 does not properly unexport display objects from its D-Bus interface when they are destroyed, which allows a local attacker to trigger a use-after-free via a specially crafted sequence of D-Bus method calls, resulting in a denial of service or potential code execution.

## References
- http://www.securityfocus.com/bid/105179
- https://gitlab.gnome.org/GNOME/gdm/issues/401
- https://usn.ubuntu.com/3737-1/
- https://www.debian.org/security/2018/dsa-4270
- https://lists.debian.org/debian-lts-announce/2018/09/msg00003.html
