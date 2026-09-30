# [C] ALPINE-CVE-2018-9127

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-9127
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-9127
Type: osv

## Affected
- Alpine:v3.11: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.12: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.13: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.14: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.15: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.16: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.17: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.18: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.19: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.20: `botan` — affected >=2.2.0 <2.5.0-r0
- Alpine:v3.21: `botan` — affected >=2.2.0 <2.5.0-r0

## Details
Botan 2.2.0 - 2.4.0 (fixed in 2.5.0) improperly handled wildcard certificates and could accept certain certificates as valid for hostnames when, under RFC 6125 rules, they should not match. This only affects certificates issued to the same domain as the host, so to impersonate a host one must already have a wildcard certificate matching other hosts in the same domain. For example, b*.example.com would match some hostnames that do not begin with a 'b' character.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-9127
