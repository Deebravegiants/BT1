# [M] Specially crafted CF.RESERVE command can lead to denial-of-service

## Summary
Severity: Medium
Advisory: CVE-2024-25116
Aliases: GHSA-wrwq-cfrx-pmg4
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-09
Source: https://osv.dev/vulnerability/CVE-2024-25116
Type: osv

## Details
RedisBloom adds a set of probabilistic data structures to Redis. Starting in version 2.0.0 and prior to version 2.4.7 and 2.6.10, authenticated users can use the `CF.RESERVE` command to trigger a runtime assertion and termination of the Redis server process. The problem is fixed in RedisBloom 2.4.7 and 2.6.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25116.json
- https://github.com/RedisBloom/RedisBloom/security/advisories/GHSA-wrwq-cfrx-pmg4
- https://nvd.nist.gov/vuln/detail/CVE-2024-25116
- https://github.com/RedisBloom/RedisBloom/commit/61d980a429050637f1af9fe919a880800a824f2a
