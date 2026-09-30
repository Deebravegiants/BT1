# [M] ALPINE-CVE-2026-14681

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-14681
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14681
Type: osv

## Affected
- Alpine:v3.21: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.22: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.24: `postgresql17` — affected >=0 <17.11-r0
- Alpine:v3.23: `postgresql18` — affected >=0 <18.5-r0
- Alpine:v3.24: `postgresql18` — affected >=0 <18.5-r0

## Details
Improper enforcement of message integrity in PostgreSQL GSSAPI support allows a user to negotiate GSSAPI contrary to pg_hba.conf rules, via initial direct TLS connection.  Despite a pg_hba.conf that appears to require GSSAPI, the connection may exchange data over TLS encryption alone.  If the TLS settings are more permissive than the GSS settings, the connection may continue with lesser protection.  Within major versions 17-18, minor versions before PostgreSQL 18.6 and 17.11 are affected.  Versions before PostgreSQL 17 are unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14681
