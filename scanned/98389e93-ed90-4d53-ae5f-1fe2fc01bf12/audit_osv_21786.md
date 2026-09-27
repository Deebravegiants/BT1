# [C] CVE-2021-46463

## Summary
Severity: Critical
Advisory: CVE-2021-46463
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-14
Source: https://osv.dev/vulnerability/CVE-2021-46463
Type: osv

## Details
njs through 0.7.1, used in NGINX, was discovered to contain a control flow hijack caused by a Type Confusion vulnerability in njs_promise_perform_then().

## References
- https://security.netapp.com/advisory/ntap-20220303-0007/
- https://github.com/nginx/njs/commit/6a40a85ff239497c6458c7dbef18f6a2736fe992
- https://github.com/nginx/njs/issues/447
