# [C] ALPINE-CVE-2024-38475

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-38475
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-38475
Type: osv

## Affected
- Alpine:v3.17: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.60-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.60-r0

## Details
Improper escaping of output in mod_rewrite in Apache HTTP Server 2.4.59 and earlier allows an attacker to map URLs to filesystem locations that are permitted to be served by the server but are not intentionally/directly reachable by any URL, resulting in code execution or source code disclosure. 

Substitutions in server context that use a backreferences or variables as the first segment of the substitution are affected.  Some unsafe RewiteRules will be broken by this change and the rewrite flag "UnsafePrefixStat" can be used to opt back in once ensuring the substitution is appropriately constrained.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-38475
