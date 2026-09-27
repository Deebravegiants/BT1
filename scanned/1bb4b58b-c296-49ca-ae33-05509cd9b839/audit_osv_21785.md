# [H] CVE-2021-46462

## Summary
Severity: High
Advisory: CVE-2021-46462
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-14
Source: https://osv.dev/vulnerability/CVE-2021-46462
Type: osv

## Details
njs through 0.7.1, used in NGINX, was discovered to contain a segmentation violation via njs_object_set_prototype in /src/njs_object.c.

## References
- https://security.netapp.com/advisory/ntap-20220303-0007/
- https://github.com/nginx/njs/commit/39e8fa1b7db1680654527f8fa0e9ee93b334ecba
- https://github.com/nginx/njs/issues/449
