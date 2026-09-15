# [C] CVE-2019-20800

## Summary
Severity: Critical
Advisory: CVE-2019-20800
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-18
Source: https://osv.dev/vulnerability/CVE-2019-20800
Type: osv

## Details
In Cherokee through 1.2.104, remote attackers can trigger an out-of-bounds write in cherokee_handler_cgi_add_env_pair in handler_cgi.c by sending many request headers, as demonstrated by a GET request with many "Host: 127.0.0.1" headers.

## References
- https://security.gentoo.org/glsa/202012-09
- https://github.com/cherokee/webserver/issues/1224
- https://logicaltrust.net/blog/2019/11/cherokee.html
