# [H] CVE-2018-14669

## Summary
Severity: High
Advisory: CVE-2018-14669
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2018-14669
Type: osv

## Details
ClickHouse MySQL client before versions 1.1.54390 had "LOAD DATA LOCAL INFILE" functionality enabled that allowed a malicious MySQL database read arbitrary files from the connected ClickHouse server.

## References
- https://clickhouse.yandex/docs/en/security_changelog/
