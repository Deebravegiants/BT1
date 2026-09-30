# [C] ALPINE-CVE-2026-42535

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-42535
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42535
Type: osv

## Affected
- Alpine:v3.21: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.68-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.68-r0

## Details
A path handling issue in mod_dav_fs in Apache 2.4.67 and earlier allows a WebDAV content author to directly manipulate trusted DAV property databases, potentially causing child process crashes.

Users are recommended to upgrade to version 2.4.68, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42535
