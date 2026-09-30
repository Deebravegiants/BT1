# [M] ALPINE-CVE-2017-2629

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-2629
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2629
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.53.0
- Alpine:v3.12: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.2: `curl` — affected >=0 <7.52.1-r1
- Alpine:v3.20: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.53.0-r0
- Alpine:v3.3: `curl` — affected >=0 <7.52.1-r1
- Alpine:v3.4: `curl` — affected >=0 <7.52.1-r2
- Alpine:v3.5: `curl` — affected >=0 <7.52.1-r2
- Alpine:v3.6: `curl` — affected >=0 <7.53.0
- Alpine:v3.7: `curl` — affected >=0 <7.53.0
- Alpine:v3.8: `curl` — affected >=0 <7.53.0
- Alpine:v3.9: `curl` — affected >=0 <7.53.0-r0

## Details
curl before 7.53.0 has an incorrect TLS Certificate Status Request extension feature that asks for a fresh proof of the server's certificate's validity in the code that checks for a test success or failure. It ends up always thinking there's valid proof, even when there is none or if the server doesn't support the TLS extension in question. This could lead to users not detecting when a server's certificate goes invalid or otherwise be mislead that the server is in a better shape than it is in reality. This flaw also exists in the command line tool (--cert-status).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2629
