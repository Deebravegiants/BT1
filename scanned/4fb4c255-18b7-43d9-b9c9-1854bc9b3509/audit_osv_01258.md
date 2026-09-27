# [C] ALPINE-CVE-2018-7584

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-7584
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7584
Type: osv

## Affected
- Alpine:v3.4: `php5` — affected >=0 <5.6.34-r0
- Alpine:v3.5: `php5` — affected >=0 <5.6.34-r0

## Details
In PHP through 5.6.33, 7.0.x before 7.0.28, 7.1.x through 7.1.14, and 7.2.x through 7.2.2, there is a stack-based buffer under-read while parsing an HTTP response in the php_stream_url_wrap_http_ex function in ext/standard/http_fopen_wrapper.c. This subsequently results in copying a large string.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7584
