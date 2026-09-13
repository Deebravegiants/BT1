# [H] CVE-2018-16056

## Summary
Severity: High
Advisory: CVE-2018-16056
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-30
Source: https://osv.dev/vulnerability/CVE-2018-16056
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.2, 2.4.0 to 2.4.8, and 2.2.0 to 2.2.16, the Bluetooth Attribute Protocol dissector could crash. This was addressed in epan/dissectors/packet-btatt.c by verifying that a dissector for a specific UUID exists.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=f98fbce64cb230e94a2cafc410a3cedad657b485
- http://www.securityfocus.com/bid/105174
- http://www.securitytracker.com/id/1041609
- https://www.debian.org/security/2018/dsa-4315
- https://www.wireshark.org/security/wnpa-sec-2018-45.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14994
