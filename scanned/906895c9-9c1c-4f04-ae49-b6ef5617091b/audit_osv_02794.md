# [C] ALPINE-CVE-2023-26463

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-26463
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-26463
Type: osv

## Affected
- Alpine:v3.17: `strongswan` — affected >=0 <5.9.10-r0
- Alpine:v3.18: `strongswan` — affected >=0 <5.9.10-r0
- Alpine:v3.19: `strongswan` — affected >=0 <5.9.10-r0
- Alpine:v3.20: `strongswan` — affected >=0 <5.9.10-r0
- Alpine:v3.21: `strongswan` — affected >=0 <5.9.10-r0
- Alpine:v3.22: `strongswan` — affected >=0 <5.9.10-r0
- Alpine:v3.23: `strongswan` — affected >=0 <5.9.10-r0
- Alpine:v3.24: `strongswan` — affected >=0 <5.9.10-r0

## Details
strongSwan 5.9.8 and 5.9.9 potentially allows remote code execution because it uses a variable named "public" for two different purposes within the same function. There is initially incorrect access control, later followed by an expired pointer dereference. One attack vector is sending an untrusted client certificate during EAP-TLS. A server is affected only if it loads plugins that implement TLS-based EAP methods (EAP-TLS, EAP-TTLS, EAP-PEAP, or EAP-TNC). This is fixed in 5.9.10.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-26463
