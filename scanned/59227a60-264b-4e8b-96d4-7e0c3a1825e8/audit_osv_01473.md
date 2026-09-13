# [H] ALPINE-CVE-2019-15892

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-15892
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15892
Type: osv

## Affected
- Alpine:v3.10: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.11: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.12: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.13: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.14: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.15: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.16: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.17: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.18: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.19: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.20: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.21: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.22: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.23: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.24: `varnish` — affected >=0 <6.2.1-r0
- Alpine:v3.8: `varnish` — affected >=0 <6.0.4-r0
- Alpine:v3.9: `varnish` — affected >=0 <6.2.1-r0

## Details
An issue was discovered in Varnish Cache before 6.0.4 LTS, and 6.1.x and 6.2.x before 6.2.1. An HTTP/1 parsing failure allows a remote attacker to trigger an assert by sending crafted HTTP/1 requests. The assert will cause an automatic restart with a clean cache, which makes it a Denial of Service attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15892
