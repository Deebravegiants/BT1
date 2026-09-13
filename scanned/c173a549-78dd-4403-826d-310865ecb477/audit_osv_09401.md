# [M] CVE-2016-9799

## Summary
Severity: Medium
Advisory: CVE-2016-9799
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2016-12-03
Source: https://osv.dev/vulnerability/CVE-2016-9799
Type: osv

## Details
In BlueZ 5.42, a buffer overflow was observed in "pklg_read_hci" function in "btsnoop.c" source file. This issue can be triggered by processing a corrupted dump file and will result in btmon crash.

## References
- http://www.securityfocus.com/bid/94652
- https://www.spinics.net/lists/linux-bluetooth/msg68898.html
