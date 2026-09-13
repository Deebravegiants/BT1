# [H] CVE-2017-13766

## Summary
Severity: High
Advisory: CVE-2017-13766
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-13766
Type: osv

## Details
In Wireshark 2.4.0 and 2.2.0 to 2.2.8, the Profinet I/O dissector could crash with an out-of-bounds write. This was addressed in plugins/profinet/packet-dcerpc-pn-io.c by adding string validation.

## References
- http://www.securityfocus.com/bid/100542
- http://www.securitytracker.com/id/1039254
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2096bc1e5078732543e0a3ee115a2ce520a72bbc
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=af7b093ca528516c14247acb545046199d30843e
- https://www.debian.org/security/2017/dsa-4060
- https://www.wireshark.org/security/wnpa-sec-2017-39.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13847
