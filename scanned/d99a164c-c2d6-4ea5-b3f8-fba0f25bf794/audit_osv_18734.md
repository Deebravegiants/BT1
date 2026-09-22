# [H] CVE-2020-35668

## Summary
Severity: High
Advisory: CVE-2020-35668
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-23
Source: https://osv.dev/vulnerability/CVE-2020-35668
Type: osv

## Details
RedisGraph 2.x through 2.2.11 has a NULL Pointer Dereference that leads to a server crash because it mishandles an unquoted string, such as an alias that has not yet been introduced.

## References
- https://github.com/RedisGraph/RedisGraph/pull/1503
- https://github.com/RedisGraph/RedisGraph/issues/1502
