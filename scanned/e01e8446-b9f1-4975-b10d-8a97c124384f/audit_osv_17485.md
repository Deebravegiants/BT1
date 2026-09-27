# [H] CVE-2020-15466

## Summary
Severity: High
Advisory: CVE-2020-15466
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-05
Source: https://osv.dev/vulnerability/CVE-2020-15466
Type: osv

## Details
In Wireshark 3.2.0 to 3.2.4, the GVCP dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-gvcp.c by ensuring that an offset increases in all situations.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=11f40896b696e4e8c7f8b2ad96028404a83a51a4
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00038.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://security.gentoo.org/glsa/202007-13
- https://www.wireshark.org/security/wnpa-sec-2020-09.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=16029
