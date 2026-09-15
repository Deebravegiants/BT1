# [C] ALPINE-CVE-2016-8705

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-8705
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-8705
Type: osv

## Affected
- Alpine:v3.4: `memcached` — affected >=0 <1.4.33-r0
- Alpine:v3.5: `memcached` — affected >=0 <1.4.33-r0

## Details
Multiple integer overflows in process_bin_update function in Memcached, which is responsible for processing multiple commands of Memcached binary protocol, can be abused to cause heap overflow and lead to remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-8705
