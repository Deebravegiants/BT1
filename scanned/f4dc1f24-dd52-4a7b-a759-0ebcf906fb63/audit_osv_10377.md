# [H] CVE-2017-15193

## Summary
Severity: High
Advisory: CVE-2017-15193
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-15193
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.1 and 2.2.0 to 2.2.9, the MBIM dissector could crash or exhaust system memory. This was addressed in epan/dissectors/packet-mbim.c by changing the memory-allocation approach.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=afb9ff7982971aba6e42472de0db4c1bedfc641b
- http://www.securityfocus.com/bid/101240
- https://www.wireshark.org/security/wnpa-sec-2017-43.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14056
- https://code.wireshark.org/review/23537
