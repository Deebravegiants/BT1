# [H] CVE-2021-42387

## Summary
Severity: High
Advisory: CVE-2021-42387
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-03-14
Source: https://osv.dev/vulnerability/CVE-2021-42387
Type: osv

## Details
Heap out-of-bounds read in Clickhouse's LZ4 compression codec when parsing a malicious query. As part of the LZ4::decompressImpl() loop, a 16-bit unsigned user-supplied value ('offset') is read from the compressed data. The offset is later used in the length of a copy operation, without checking the upper bounds of the source of the copy operation.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00002.html
- https://jfrog.com/blog/7-rce-and-dos-vulnerabilities-found-in-clickhouse-dbms
