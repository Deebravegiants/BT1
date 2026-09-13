# [C] CVE-2019-11839

## Summary
Severity: Critical
Advisory: CVE-2019-11839
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2019-11839
Type: osv

## Details
njs through 0.3.1, used in NGINX, has a heap-based buffer overflow in Array.prototype.push after a resize, related to njs_array_prototype_push in njs/njs_array.c, because of njs_array_expand size mishandling.

## References
- https://github.com/nginx/njs/issues/152
