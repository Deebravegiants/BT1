# [H] CVE-2018-9256

## Summary
Severity: High
Advisory: CVE-2018-9256
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9256
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.5 and 2.2.0 to 2.2.13, the LWAPP dissector could crash. This was addressed in epan/dissectors/packet-lwapp.c by limiting the encapsulation levels to restrict the recursion depth.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=dac48f148538c706c446e5105d84ebcb54587528
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-20.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14467
