# [H] CVE-2016-10517

## Summary
Severity: High
Advisory: CVE-2016-10517
CVSS: 7.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/CVE-2016-10517
Type: osv

## Details
networking.c in Redis before 3.2.7 allows "Cross Protocol Scripting" because it lacks a check for POST and Host: strings, which are not valid in the Redis protocol (but commonly occur when an attack triggers an HTTP request to the Redis TCP port).

## References
- http://www.securityfocus.com/bid/101572
- https://github.com/antirez/redis/commit/874804da0c014a7d704b3d285aa500098a931f50
- https://raw.githubusercontent.com/antirez/redis/3.2/00-RELEASENOTES
- https://www.reddit.com/r/redis/comments/5r8wxn/redis_327_is_out_important_security_fixes_inside/
