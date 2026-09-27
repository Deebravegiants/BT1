# [H] ALPINE-CVE-2017-11185

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-11185
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11185
Type: osv

## Affected
- Alpine:v3.3: `strongswan` — affected >=0 <5.3.5-r4
- Alpine:v3.4: `strongswan` — affected >=0 <5.4.0-r3
- Alpine:v3.5: `strongswan` — affected >=0 <5.5.3-r1
- Alpine:v3.6: `strongswan` — affected >=0 <5.5.3-r1

## Details
The gmp plugin in strongSwan before 5.6.0 allows remote attackers to cause a denial of service (NULL pointer dereference and daemon crash) via a crafted RSA signature.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11185
