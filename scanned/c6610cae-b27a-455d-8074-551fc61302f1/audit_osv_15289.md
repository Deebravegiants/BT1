# [M] CVE-2019-15024

## Summary
Severity: Medium
Advisory: CVE-2019-15024
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-15024
Type: osv

## Details
In all versions of ClickHouse before 19.14.3, an attacker having write access to ZooKeeper and who is able to run a custom server available from the network where ClickHouse runs, can create a custom-built malicious server that will act as a ClickHouse replica and register it in ZooKeeper. When another replica will fetch data part from the malicious replica, it can force clickhouse-server to write to arbitrary path on filesystem.

## References
- https://clickhouse.yandex/docs/en/security_changelog/
