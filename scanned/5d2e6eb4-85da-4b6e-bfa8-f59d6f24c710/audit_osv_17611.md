# [M] CVE-2020-17489

## Summary
Severity: Medium
Advisory: CVE-2020-17489
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-08-11
Source: https://osv.dev/vulnerability/CVE-2020-17489
Type: osv

## Details
An issue was discovered in certain configurations of GNOME gnome-shell through 3.36.4. When logging out of an account, the password box from the login dialog reappears with the password still visible. If the user had decided to have the password shown in cleartext at login time, it is then visible for a brief moment upon a logout. (If the password were never shown in cleartext, only the password length is revealed.)

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00014.html
- https://security.gentoo.org/glsa/202009-08
- https://usn.ubuntu.com/4464-1/
- https://gitlab.gnome.org/GNOME/gnome-shell/-/issues/2997
