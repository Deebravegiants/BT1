# [H] ALPINE-CVE-2023-43622

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-43622
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-43622
Type: osv

## Affected
- Alpine:v3.15: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.58-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.58-r0

## Details
An attacker, opening a HTTP/2 connection with an initial window size of 0, was able to block handling of that connection indefinitely in Apache HTTP Server. This could be used to exhaust worker resources in the server, similar to the well known "slow loris" attack pattern.
This has been fixed in version 2.4.58, so that such connection are terminated properly after the configured connection timeout.

This issue affects Apache HTTP Server: from 2.4.55 through 2.4.57.

Users are recommended to upgrade to version 2.4.58, which fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-43622
