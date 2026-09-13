# [H] RedisBloom heap buffer overflow in CF.LOADCHUNK command

## Summary
Severity: High
Advisory: CVE-2024-25115
Aliases: GHSA-w583-p2wh-4vj5
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-09
Source: https://osv.dev/vulnerability/CVE-2024-25115
Type: osv

## Details
RedisBloom adds a set of probabilistic data structures to Redis. Starting in version 2.0.0 and prior to version 2.4.7 and 2.6.10, specially crafted `CF.LOADCHUNK` commands may be used by authenticated users to perform heap overflow, which may lead to remote code execution. The problem is fixed in RedisBloom 2.4.7 and 2.6.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25115.json
- https://github.com/RedisBloom/RedisBloom/security/advisories/GHSA-w583-p2wh-4vj5
- https://nvd.nist.gov/vuln/detail/CVE-2024-25115
- https://github.com/RedisBloom/RedisBloom/commit/2f3b38394515fc6c9b130679bcd2435a796a49ad
