# [C] ALPINE-CVE-2020-11945

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-11945
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11945
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=3.0 <4.11-r0
- Alpine:v3.11: `squid` — affected >=3.0 <4.11-r0
- Alpine:v3.9: `squid` — affected >=3.0 <4.11-r0

## Details
An issue was discovered in Squid before 5.0.2. A remote attacker can replay a sniffed Digest Authentication nonce to gain access to resources that are otherwise forbidden. This occurs because the attacker can overflow the nonce reference counter (a short integer). Remote code execution may occur if the pooled token credentials are freed (instead of replayed as valid credentials).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11945
