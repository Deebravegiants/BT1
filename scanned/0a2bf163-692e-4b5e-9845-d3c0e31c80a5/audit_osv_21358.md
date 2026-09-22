# [M] CVE-2021-42390

## Summary
Severity: Medium
Advisory: CVE-2021-42390
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-14
Source: https://osv.dev/vulnerability/CVE-2021-42390
Type: osv

## Details
Divide-by-zero in Clickhouse's DeltaDouble compression codec when parsing a malicious query. The first byte of the compressed buffer is used in a modulo operation without being checked for 0.

## References
- https://jfrog.com/blog/7-rce-and-dos-vulnerabilities-found-in-clickhouse-dbms
