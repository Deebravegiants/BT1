# [M] ALPINE-CVE-2025-32802

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-32802
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-05-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-32802
Type: osv

## Affected
- Alpine:v3.22: `kea` — affected >=0 <2.6.3-r0
- Alpine:v3.23: `kea` — affected >=0 <2.6.3-r0
- Alpine:v3.24: `kea` — affected >=0 <2.6.3-r0

## Details
Kea configuration and API directives can be used to overwrite arbitrary files, subject to permissions granted to Kea.  Many common configurations run Kea as root, leave the API entry points unsecured by default, and/or place the control sockets in insecure paths.
This issue affects Kea versions 2.4.0 through 2.4.1, 2.6.0 through 2.6.2, and 2.7.0 through 2.7.8.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-32802
