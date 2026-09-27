# [H] CVE-2020-14147

## Summary
Severity: High
Advisory: CVE-2020-14147
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14147
Type: osv

## Details
An integer overflow in the getnum function in lua_struct.c in Redis before 6.0.3 allows context-dependent attackers with permission to run Lua code in a Redis session to cause a denial of service (memory corruption and application crash) or possibly bypass intended sandbox restrictions via a large number, which triggers a stack-based buffer overflow. NOTE: this issue exists because of a CVE-2015-8080 regression.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00058.html
- https://security.gentoo.org/glsa/202008-17
- https://www.debian.org/security/2020/dsa-4731
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://github.com/antirez/redis/commit/ef764dde1cca2f25d00686673d1bc89448819571
- https://github.com/antirez/redis/pull/6875
