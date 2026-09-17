# [H] CVE-2020-11724

## Summary
Severity: High
Advisory: CVE-2020-11724
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-04-12
Source: https://osv.dev/vulnerability/CVE-2020-11724
Type: osv

## Details
An issue was discovered in OpenResty before 1.15.8.4. ngx_http_lua_subrequest.c allows HTTP request smuggling, as demonstrated by the ngx.location.capture API.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00014.html
- https://security.netapp.com/advisory/ntap-20210129-0002/
- https://www.debian.org/security/2020/dsa-4750
- https://github.com/openresty/lua-nginx-module/commit/9ab38e8ee35fc08a57636b1b6190dca70b0076fa
- https://github.com/openresty/openresty/blob/4e8b4c395f842a078e429c80dd063b2323999957/patches/ngx_http_lua-0.10.15-fix_location_capture_content_length_chunked.patch
