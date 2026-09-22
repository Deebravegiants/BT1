# [H] CVE-2019-16319

## Summary
Severity: High
Advisory: CVE-2019-16319
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-15
Source: https://osv.dev/vulnerability/CVE-2019-16319
Type: osv

## Details
In Wireshark 3.0.0 to 3.0.3 and 2.6.0 to 2.6.10, the Gryphon dissector could go into an infinite loop. This was addressed in plugins/epan/gryphon/packet-gryphon.c by checking for a message length of zero.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=02ddd49885c6a09e936a76aceb726ed06539704a
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://www.wireshark.org/security/wnpa-sec-2019-21.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=16020
