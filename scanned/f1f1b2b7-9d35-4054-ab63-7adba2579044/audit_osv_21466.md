# [H] CVE-2021-43305

## Summary
Severity: High
Advisory: CVE-2021-43305
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-14
Source: https://osv.dev/vulnerability/CVE-2021-43305
Type: osv

## Details
Heap buffer overflow in Clickhouse's LZ4 compression codec when parsing a malicious query. There is no verification that the copy operations in the LZ4::decompressImpl loop and especially the arbitrary copy operation wildCopy<copy_amount>(op, ip, copy_end), don’t exceed the destination buffer’s limits. This issue is very similar to CVE-2021-43304, but the vulnerable copy operation is in a different wildCopy call.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00002.html
- https://jfrog.com/blog/7-rce-and-dos-vulnerabilities-found-in-clickhouse-dbms
