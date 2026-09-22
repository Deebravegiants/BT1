# [C] CVE-2018-11218

## Summary
Severity: Critical
Advisory: CVE-2018-11218
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-17
Source: https://osv.dev/vulnerability/CVE-2018-11218
Type: osv

## Details
Memory Corruption was discovered in the cmsgpack library in the Lua subsystem in Redis before 3.2.12, 4.x before 4.0.10, and 5.x before 5.0 RC2 because of stack-based buffer overflows.

## References
- http://www.securityfocus.com/bid/104553
- https://access.redhat.com/errata/RHSA-2019:0052
- https://access.redhat.com/errata/RHSA-2019:0094
- https://access.redhat.com/errata/RHSA-2019:1860
- https://github.com/antirez/redis/issues/5017
- https://raw.githubusercontent.com/antirez/redis/4.0/00-RELEASENOTES
- https://raw.githubusercontent.com/antirez/redis/5.0/00-RELEASENOTES
- https://security.gentoo.org/glsa/201908-04
- https://www.debian.org/security/2018/dsa-4230
- https://github.com/antirez/redis/commit/52a00201fca331217c3b4b8b634f6a0f57d6b7d3
- https://github.com/antirez/redis/commit/5ccb6f7a791bf3490357b00a898885759d98bab0
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://antirez.com/news/119
