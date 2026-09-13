# [H] ALPINE-CVE-2024-39573

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-39573
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-39573
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
Potential SSRF in mod_rewrite in Apache HTTP Server 2.4.59 and earlier allows an attacker to cause unsafe RewriteRules to unexpectedly setup URL's to be handled by mod_proxy.
Users are recommended to upgrade to version 2.4.60, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-39573
