# [H] RedisTimeSeries Integer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-51480
Aliases: GHSA-73x6-fqww-x8rg
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-51480
Type: osv

## Details
RedisTimeSeries is a time-series database (TSDB) module for Redis, by Redis. Executing one of these commands TS.QUERYINDEX, TS.MGET, TS.MRAGE, TS.MREVRANGE by an authenticated user, using specially crafted command arguments may cause an integer overflow, a subsequent heap overflow, and potentially lead to remote code execution. This vulnerability is fixed in 1.6.20, 1.8.15, 1.10.15, and 1.12.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51480.json
- https://github.com/RedisTimeSeries/RedisTimeSeries/security/advisories/GHSA-73x6-fqww-x8rg
- https://nvd.nist.gov/vuln/detail/CVE-2024-51480
