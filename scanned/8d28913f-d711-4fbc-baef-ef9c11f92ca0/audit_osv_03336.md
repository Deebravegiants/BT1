# [H] ALPINE-CVE-2025-55753

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-55753
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-55753
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.66-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.66-r0

## Details
An integer overflow in the case of failed ACME certificate renewal leads, after a number of failures (~30 days in default configurations), to the backoff timer becoming 0. Attempts to renew the certificate then are repeated without delays until it succeeds.

This issue affects Apache HTTP Server: from 2.4.30 before 2.4.66.


Users are recommended to upgrade to version 2.4.66, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-55753
