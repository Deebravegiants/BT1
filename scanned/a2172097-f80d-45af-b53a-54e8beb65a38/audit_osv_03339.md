# [H] ALPINE-CVE-2025-58060

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-58060
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58060
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.13-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.13-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.12 and earlier, when the `AuthType` is set to anything but `Basic`, if the request contains an `Authorization: Basic ...` header, the password is not checked. This results in authentication bypass. Any configuration that allows an `AuthType` that is not `Basic` is affected. Version 2.4.13 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58060
