# [H] CVE-2020-11647

## Summary
Severity: High
Advisory: CVE-2020-11647
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-10
Source: https://osv.dev/vulnerability/CVE-2020-11647
Type: osv

## Details
In Wireshark 3.2.0 to 3.2.2, 3.0.0 to 3.0.9, and 2.6.0 to 2.6.15, the BACapp dissector could crash. This was addressed in epan/dissectors/packet-bacapp.c by limiting the amount of recursion.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6f56fc9496db158218243ea87e3660c874a0bab0
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://security.gentoo.org/glsa/202007-13
- https://www.wireshark.org/security/wnpa-sec-2020-07.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=16474
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00038.html
