# [H] CVE-2018-14668

## Summary
Severity: High
Advisory: CVE-2018-14668
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2018-14668
Type: osv

## Details
In ClickHouse before 1.1.54388, "remote" table function allowed arbitrary symbols in "user", "password" and "default_database" fields which led to Cross Protocol Request Forgery Attacks.

## References
- https://clickhouse.yandex/docs/en/security_changelog/
