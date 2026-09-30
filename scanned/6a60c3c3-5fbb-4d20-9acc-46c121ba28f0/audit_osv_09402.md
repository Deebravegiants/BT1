# [M] CVE-2016-9800

## Summary
Severity: Medium
Advisory: CVE-2016-9800
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2016-12-03
Source: https://osv.dev/vulnerability/CVE-2016-9800
Type: osv

## Details
In BlueZ 5.42, a buffer overflow was observed in "pin_code_reply_dump" function in "tools/parser/hci.c" source file. The issue exists because "pin" array is overflowed by supplied parameter due to lack of boundary checks on size of the buffer from frame "pin_code_reply_cp *cp" parameter.

## References
- http://www.securityfocus.com/bid/94652
- https://www.spinics.net/lists/linux-bluetooth/msg68892.html
