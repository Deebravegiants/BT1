# [H] CVE-2018-9257

## Summary
Severity: High
Advisory: CVE-2018-9257
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9257
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.5, the CQL dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-cql.c by checking for a nonzero number of columns.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=d7a9501b0439a5dbf24016a95b4896170d789dc2
- https://www.wireshark.org/security/wnpa-sec-2018-22.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14530
