# [H] ALPINE-CVE-2026-29169

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-29169
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-29169
Type: osv

## Affected
- Alpine:v3.20: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.67-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.67-r0

## Details
A NULL pointer dereference in mod_dav_lock in Apache HTTP Server 2.4.66 and earlier may allow an attacker to crash the server with a malicious request.mod_dav_lock is not used internally by mod_dav or mod_dav_fs.

The only known use-case for mod_dav_lock was mod_dav_svn from Apache Subversion earlier than version 1.2.0.

Users are recommended to upgrade to version 2.4.66, which fixes this issue, or remove mod_dav_lock.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-29169
