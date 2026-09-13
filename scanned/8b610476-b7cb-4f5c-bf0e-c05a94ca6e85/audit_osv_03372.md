# [M] ALPINE-CVE-2025-65082

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-65082
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-65082
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.66-r0

## Details
Improper Neutralization of Escape, Meta, or Control Sequences vulnerability in Apache HTTP Server through environment variables set via the Apache configuration unexpectedly superseding variables calculated by the server for CGI programs.

This issue affects Apache HTTP Server from 2.4.0 through 2.4.65.

Users are recommended to upgrade to version 2.4.66 which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-65082
