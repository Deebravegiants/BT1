# [H] CVE-2018-12453

## Summary
Severity: High
Advisory: CVE-2018-12453
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-16
Source: https://osv.dev/vulnerability/CVE-2018-12453
Type: osv

## Details
Type confusion in the xgroupCommand function in t_stream.c in redis-server in Redis before 5.0 allows remote attackers to cause denial-of-service via an XGROUP command in which the key is not a stream.

## References
- https://github.com/antirez/redis/commit/c04082cf138f1f51cedf05ee9ad36fb6763cafc6
- https://gist.github.com/fakhrizulkifli/34a56d575030682f6c564553c53b82b5
- https://www.exploit-db.com/exploits/44908/
