# [M] CVE-2016-9803

## Summary
Severity: Medium
Advisory: CVE-2016-9803
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2016-12-03
Source: https://osv.dev/vulnerability/CVE-2016-9803
Type: osv

## Details
In BlueZ 5.42, an out-of-bounds read was observed in "le_meta_ev_dump" function in "tools/parser/hci.c" source file. This issue exists because 'subevent' (which is used to read correct element from 'ev_le_meta_str' array) is overflowed.

## References
- http://www.securityfocus.com/bid/94652
- https://www.spinics.net/lists/linux-bluetooth/msg68892.html
