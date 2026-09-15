# [H] CVE-2019-11837

## Summary
Severity: High
Advisory: CVE-2019-11837
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2019-11837
Type: osv

## Details
njs through 0.3.1, used in NGINX, has a segmentation fault in String.prototype.toBytes for negative arguments, related to nxt_utf8_next in nxt/nxt_utf8.h and njs_string_offset in njs/njs_string.c.

## References
- https://github.com/nginx/njs/issues/155
