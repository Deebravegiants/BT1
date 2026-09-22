# [H] Redis - Heap Out-of-Bounds Read in Cluster Bus PING Message Handler

## Summary
Severity: High
Advisory: CVE-2026-72568
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72568
Type: osv

## Details
An out-of-bounds read vulnerability in Redis through 8.8.1 allows an adjacent unauthenticated attacker to cause denial of service or information disclosure by sending a specially crafted PING message to the Redis Cluster Bus port.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72568.json
- https://github.com/redis/redis
- https://nvd.nist.gov/vuln/detail/CVE-2026-72568
- https://redis.io/
