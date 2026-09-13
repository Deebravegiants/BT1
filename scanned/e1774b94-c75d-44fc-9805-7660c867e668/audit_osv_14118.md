# [H] CVE-2018-7320

## Summary
Severity: High
Advisory: CVE-2018-7320
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7320
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, the SIGCOMP protocol dissector could crash. This was addressed in epan/dissectors/packet-sigcomp.c by validating operand offsets.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=015e3399390b8b5cfbfcfcda30589983ab6cc129
- http://www.securityfocus.com/bid/103160
- https://www.debian.org/security/2018/dsa-4217
- https://www.wireshark.org/security/wnpa-sec-2018-10.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14398
