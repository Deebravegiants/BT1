# [C] ALPINE-CVE-2024-38474

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-38474
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-38474
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
Substitution encoding issue in mod_rewrite in Apache HTTP Server 2.4.59 and earlier allows attacker to execute scripts in
directories permitted by the configuration but not directly reachable by any URL or source disclosure of scripts meant to only to be executed as CGI.

Users are recommended to upgrade to version 2.4.60, which fixes this issue.

Some RewriteRules that capture and substitute unsafely will now fail unless rewrite flag "UnsafeAllow3F" is specified.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-38474
