# [M] ALPINE-CVE-2024-42491

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-42491
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-42491
Type: osv

## Affected
- Alpine:v3.17: `asterisk` — affected >=20.0.0 <18.24.3-r0
- Alpine:v3.18: `asterisk` — affected >=20.0.0 <18.24.3-r0
- Alpine:v3.19: `asterisk` — affected >=20.0.0 <20.9.3-r0
- Alpine:v3.20: `asterisk` — affected >=20.0.0 <20.9.3-r0
- Alpine:v3.21: `asterisk` — affected >=20.0.0 <20.9.3-r0
- Alpine:v3.22: `asterisk` — affected >=20.0.0 <20.9.3-r0
- Alpine:v3.23: `asterisk` — affected >=20.0.0 <20.9.3-r0
- Alpine:v3.24: `asterisk` — affected >=20.0.0 <20.9.3-r0

## Details
Asterisk is an open-source private branch exchange (PBX). Prior to versions 18.24.3, 20.9.3, and 21.4.3 of Asterisk and versions 18.9-cert12 and 20.7-cert2 of certified-asterisk, if Asterisk attempts to send a SIP request to a URI whose host portion starts with `.1` or `[.1]`, and res_resolver_unbound is loaded, Asterisk will crash with a SEGV. To receive a patch, users should upgrade to one of the following versions: 18.24.3, 20.9.3, 21.4.3, certified-18.9-cert12, certified-20.7-cert2. Two workarounds are available. Disable res_resolver_unbound by setting `noload = res_resolver_unbound.so` in modules.conf, or set `rewrite_contact = yes` on all PJSIP endpoints. NOTE: This may not be appropriate for all Asterisk configurations.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-42491
