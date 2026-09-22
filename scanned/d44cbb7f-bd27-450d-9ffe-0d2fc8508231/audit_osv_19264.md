# [H] CVE-2020-9429

## Summary
Severity: High
Advisory: CVE-2020-9429
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-9429
Type: osv

## Details
In Wireshark 3.2.0 to 3.2.1, the WireGuard dissector could crash. This was addressed in epan/dissectors/packet-wireguard.c by handling the situation where a certain data structure intentionally has a NULL value.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=73c5fff899f253c44a72657048aec7db6edee571
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a2530f740d67d41908e84434bb5ec99480c2ac2e
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://security.gentoo.org/glsa/202007-13
- https://www.wireshark.org/security/wnpa-sec-2020-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=16394
