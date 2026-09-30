# [H] ALPINE-CVE-2016-5419

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-5419
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-08-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-5419
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.11: `curl` — affected >=0 <7.50.1
- Alpine:v3.12: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.13: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.14: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.15: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.16: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.18: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.19: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.2: `curl` — affected >=0 <7.49.1-r1
- Alpine:v3.20: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.21: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.22: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.23: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.24: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.3: `curl` — affected >=0 <7.49.1-r1
- Alpine:v3.4: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.5: `curl` — affected >=0 <7.50.1-r0
- Alpine:v3.6: `curl` — affected >=0 <7.50.1
- Alpine:v3.7: `curl` — affected >=0 <7.50.1
- Alpine:v3.8: `curl` — affected >=0 <7.50.1
- Alpine:v3.9: `curl` — affected >=0 <7.50.1-r0

## Details
curl and libcurl before 7.50.1 do not prevent TLS session resumption when the client certificate has changed, which allows remote attackers to bypass intended restrictions by resuming a session.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-5419
