# [C] CVE-2017-20005

## Summary
Severity: Critical
Advisory: CVE-2017-20005
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-06
Source: https://osv.dev/vulnerability/CVE-2017-20005
Type: osv

## Details
NGINX before 1.13.6 has a buffer overflow for years that exceed four digits, as demonstrated by a file with a modification date in 1969 that causes an integer overflow (or a false modification date far in the future), when encountered by the autoindex module.

## References
- http://nginx.org/en/CHANGES
- https://lists.debian.org/debian-lts-announce/2021/06/msg00009.html
- https://security.netapp.com/advisory/ntap-20210805-0006/
- https://github.com/nginx/nginx/commit/0206ebe76f748bb39d9de4dd4b3fce777fdfdccf
- https://github.com/nginx/nginx/commit/b900cc28fcbb4cf5a32ab62f80b59292e1c85b4b
- https://trac.nginx.org/nginx/ticket/1368
