# [C] Redis TLS pending-data list use-after-free

## Summary
Severity: Critical
Advisory: CVE-2026-81934
CVSS: 9.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81934
Type: osv

## Details
Redis contains a use-after-free vulnerability in the 'tlsProcessPendingData()' function, which handles the TLS pending-data list if Redis is configured with TLS support. A remote, unauthenticated attacker may be able to execute arbitrary commands with the privileges of the Redis server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81934.json
- https://github.com/redis/redis/releases/tag/6.2.24
- https://github.com/redis/redis/releases/tag/7.2.16
- https://github.com/redis/redis/releases/tag/7.4.11
- https://github.com/redis/redis/releases/tag/8.10.1
- https://github.com/redis/redis/releases/tag/8.2.9
- https://github.com/redis/redis/releases/tag/8.4.6
- https://github.com/redis/redis/releases/tag/8.6.6
- https://github.com/redis/redis/releases/tag/8.8.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-81934
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-26-239-01.json
- https://raw.githubusercontent.com/redis/redis/6.2/00-RELEASENOTES
- https://raw.githubusercontent.com/redis/redis/7.2/00-RELEASENOTES
- https://raw.githubusercontent.com/redis/redis/7.4/00-RELEASENOTES
- https://raw.githubusercontent.com/redis/redis/8.10/00-RELEASENOTES
- https://raw.githubusercontent.com/redis/redis/8.2/00-RELEASENOTES
- https://raw.githubusercontent.com/redis/redis/8.4/00-RELEASENOTES
- https://raw.githubusercontent.com/redis/redis/8.6/00-RELEASENOTES
- https://raw.githubusercontent.com/redis/redis/8.8/00-RELEASENOTES
- https://redis.io/docs/latest/operate/rs/release-notes/rs-7-22-releases/rs-7-22-2-179/
