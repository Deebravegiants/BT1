# [H] CVE-2026-66373

## Summary
Severity: High
Advisory: CVE-2026-66373
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-66373
Type: osv

## Details
Redis before 8.8.0, in the unusual case where an authenticated attacker can execute RESTORE, allows remote code execution via a RESTORE payload where the same NACK (pending entry) is referenced by more than one consumer, because deleting both consumers via XGROUP DELCONSUMER leads to a double free. NOTE: this issue exists because of an incomplete fix for CVE-2026-25243.

## References
- https://github.com/redis/redis/compare/8.6.4...8.8.0
- https://lists.debian.org/debian-lts-announce/2026/08/msg00012.html
- https://news.ycombinator.com/item?id=49024938
- https://x.com/Fried_rice/status/2080059356322918777
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66373
- https://github.com/redis/redis/pull/15081
- https://github.com/berabuddies/redis-poc
