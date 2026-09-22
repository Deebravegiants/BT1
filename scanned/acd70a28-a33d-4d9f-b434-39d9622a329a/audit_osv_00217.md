# [H] ALPINE-CVE-2016-7141

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7141
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7141
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.11: `curl` — affected >=0 <7.50.2
- Alpine:v3.12: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.13: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.14: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.15: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.16: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.17: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.18: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.19: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.2: `curl` — affected >=0 <7.49.1-r2
- Alpine:v3.20: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.21: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.22: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.23: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.24: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.3: `curl` — affected >=0 <7.49.1-r2
- Alpine:v3.4: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.5: `curl` — affected >=0 <7.50.2-r0
- Alpine:v3.6: `curl` — affected >=0 <7.50.2
- Alpine:v3.7: `curl` — affected >=0 <7.50.2
- Alpine:v3.8: `curl` — affected >=0 <7.50.2
- Alpine:v3.9: `curl` — affected >=0 <7.50.2-r1

## Details
curl and libcurl before 7.50.2, when built with NSS and the libnsspem.so library is available at runtime, allow remote attackers to hijack the authentication of a TLS connection by leveraging reuse of a previously loaded client certificate from file for a connection for which no certificate has been set, a different vulnerability than CVE-2016-5420.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7141
