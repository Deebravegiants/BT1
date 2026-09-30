# [M] CVE-2017-6200

## Summary
Severity: Medium
Advisory: CVE-2017-6200
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2017-6200
Type: osv

## Details
Sandstorm before build 0.203 allows remote attackers to read any specified file under /etc or /run via the sandbox backup function. The root cause is that the findFilesToZip function doesn't filter Line Feed (\n) characters in a directory name.

## References
- https://github.com/sandstorm-io/sandstorm/blob/v0.202/src/sandstorm/backup.c%2B%2B#L271
- https://sandstorm.io/news/2017-03-02-security-review
- https://github.com/sandstorm-io/sandstorm/commit/4ea8df7403381d9b657b121b3c98d8081b27414d
- https://github.com/sandstorm-io/sandstorm/commit/6e8572ea8bb56d0216bb1b410e5040edc051b120
- https://devco.re/blog/2018/01/26/Sandstorm-Security-Review-CVE-2017-6200-en/
