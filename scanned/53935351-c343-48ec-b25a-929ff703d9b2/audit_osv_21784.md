# [C] CVE-2021-46461

## Summary
Severity: Critical
Advisory: CVE-2021-46461
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-14
Source: https://osv.dev/vulnerability/CVE-2021-46461
Type: osv

## Details
njs through 0.7.0, used in NGINX, was discovered to contain an out-of-bounds array access via njs_vmcode_typeof in /src/njs_vmcode.c.

## References
- https://security.netapp.com/advisory/ntap-20220303-0007/
- https://github.com/nginx/njs/commit/d457c9545e7e71ebb5c0479eb16b9d33175855e2
- https://github.com/nginx/njs/issues/450
