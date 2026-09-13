# [H] ALPINE-CVE-2024-47252

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-47252
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47252
Type: osv

## Affected
- Alpine:v3.19: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.64-r0

## Details
Insufficient escaping of user-supplied data in mod_ssl in Apache HTTP Server 2.4.63 and earlier allows an untrusted SSL/TLS client to insert escape characters into log files in some configurations.

In a logging configuration where CustomLog is used with "%{varname}x" or "%{varname}c" to log variables provided by mod_ssl such as SSL_TLS_SNI, no escaping is performed by either mod_log_config or mod_ssl and unsanitized data provided by the client may appear in log files.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47252
