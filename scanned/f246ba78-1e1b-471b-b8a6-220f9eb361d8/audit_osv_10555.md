# [H] CVE-2017-17083

## Summary
Severity: High
Advisory: CVE-2017-17083
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/CVE-2017-17083
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.2 and 2.2.0 to 2.2.10, the NetBIOS dissector could crash. This was addressed in epan/dissectors/packet-netbios.c by ensuring that write operations are bounded by the beginning of a buffer.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=79768d63d14fbce6bf7fb4d4a1c86be0c5205eb3
- https://lists.debian.org/debian-lts-announce/2017/12/msg00029.html
- http://www.securityfocus.com/bid/102029
- https://www.debian.org/security/2017/dsa-4060
- https://www.wireshark.org/security/wnpa-sec-2017-48.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14249
