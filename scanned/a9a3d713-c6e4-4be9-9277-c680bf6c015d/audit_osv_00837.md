# [H] ALPINE-CVE-2017-9951

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9951
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9951
Type: osv

## Affected
- Alpine:v3.3: `memcached` — affected >=0 <1.4.33-r1
- Alpine:v3.4: `memcached` — affected >=0 <1.4.33-r1
- Alpine:v3.5: `memcached` — affected >=0 <1.4.33-r1
- Alpine:v3.6: `memcached` — affected >=0 <1.4.36-r1

## Details
The try_read_command function in memcached.c in memcached before 1.4.39 allows remote attackers to cause a denial of service (segmentation fault) via a request to add/set a key, which makes a comparison between signed and unsigned int and triggers a heap-based buffer over-read. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-8705.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9951
