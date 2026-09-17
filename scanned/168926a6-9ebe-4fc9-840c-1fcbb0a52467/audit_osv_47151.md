# [H] CVE-2015-9542

## Summary
Severity: High
Advisory: CVE-2015-9542
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/CVE-2015-9542
Type: osv

## Details
add_password in pam_radius_auth.c in pam_radius 1.4.0 does not correctly check the length of the input password, and is vulnerable to a stack-based buffer overflow during memcpy(). An attacker could send a crafted password to an application (loading the pam_radius library) and crash it. Arbitrary code execution might be possible, depending on the application, C library, compiler, and other factors.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2015-9542
- https://github.com/FreeRADIUS/pam_radius/commit/01173ec2426627dbb1e0d96c06c3ffa0b14d36d0
- https://lists.debian.org/debian-lts-announce/2020/02/msg00023.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00000.html
- https://usn.ubuntu.com/4290-1/
- https://usn.ubuntu.com/4290-2/
- https://lists.debian.org/debian-lts-announce/2020/02/msg00023.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00000.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2015-9542
- https://github.com/FreeRADIUS/pam_radius/commit/01173ec2426627dbb1e0d96c06c3ffa0b14d36d0
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2015-9542
