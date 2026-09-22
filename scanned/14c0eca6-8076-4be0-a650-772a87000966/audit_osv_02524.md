# [C] ALPINE-CVE-2022-28615

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-28615
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-28615
Type: osv

## Affected
- Alpine:v3.13: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.54-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.54-r0

## Details
Apache HTTP Server 2.4.53 and earlier may crash or disclose information due to a read beyond bounds in ap_strcmp_match() when provided with an extremely large input buffer. While no code distributed with the server can be coerced into such a call, third-party modules or lua scripts that use ap_strcmp_match() may hypothetically be affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-28615
