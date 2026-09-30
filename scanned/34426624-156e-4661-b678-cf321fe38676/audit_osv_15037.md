# [C] CVE-2019-13067

## Summary
Severity: Critical
Advisory: CVE-2019-13067
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/CVE-2019-13067
Type: osv

## Details
njs through 0.3.3, used in NGINX, has a buffer over-read in nxt_utf8_decode in nxt/nxt_utf8.c. This issue occurs after the fix for CVE-2019-12207 is in place.

## References
- https://github.com/nginx/njs/issues/183
