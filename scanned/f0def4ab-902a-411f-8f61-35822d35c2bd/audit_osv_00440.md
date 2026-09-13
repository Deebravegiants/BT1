# [H] ALPINE-CVE-2017-12425

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12425
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12425
Type: osv

## Affected
- Alpine:v3.10: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.11: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.12: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.13: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.14: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.15: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.16: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.17: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.18: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.19: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.20: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.21: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.22: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.23: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.24: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.3: `varnish` — affected >=0 <4.1.2-r2
- Alpine:v3.4: `varnish` — affected >=0 <4.1.2-r4
- Alpine:v3.5: `varnish` — affected >=0 <4.1.3-r1
- Alpine:v3.6: `varnish` — affected >=0 <4.1.3-r1
- Alpine:v3.7: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.8: `varnish` — affected >=0 <5.1.3-r0
- Alpine:v3.9: `varnish` — affected >=0 <5.1.3-r0

## Details
An issue was discovered in Varnish HTTP Cache 4.0.1 through 4.0.4, 4.1.0 through 4.1.7, 5.0.0, and 5.1.0 through 5.1.2. A wrong if statement in the varnishd source code means that particular invalid requests from the client can trigger an assert, related to an Integer Overflow. This causes the varnishd worker process to abort and restart, losing the cached contents in the process. An attacker can therefore crash the varnishd worker process on demand and effectively keep it from serving content - a Denial-of-Service attack. The specific source-code filename containing the incorrect statement varies across releases.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12425
