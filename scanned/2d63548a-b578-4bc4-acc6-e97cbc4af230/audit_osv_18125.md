# [M] CVE-2020-24275

## Summary
Severity: Medium
Advisory: CVE-2020-24275
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/CVE-2020-24275
Type: osv

## Details
A HTTP response header injection vulnerability in Swoole v4.5.2 allows attackers to execute arbitrary code via supplying a crafted URL.

## References
- https://github.com/swoole/swoole-src/pull/3539
- https://github.com/swoole/swoole-src/pull/3545
- https://portswigger.net/kb/issues/00200200_http-response-header-injection
- https://blog.cal1.cn/post/HTTP%20Response%20Header%20Injection%20in%20Swoole%3C%3D4.5.2
