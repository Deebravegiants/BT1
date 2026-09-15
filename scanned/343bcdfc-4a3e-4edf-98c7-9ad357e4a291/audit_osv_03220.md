# [H] ALPINE-CVE-2025-23083

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-23083
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.7 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-23083
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <22.13.1-r0

## Details
With the aid of the diagnostics_channel utility, an event can be hooked into whenever a worker thread is created. This is not limited only to workers but also exposes internal workers, where an instance of them can be fetched, and its constructor can be grabbed and reinstated for malicious usage. 

This vulnerability affects Permission Model users (--permission) on Node.js v20, v22, and v23.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-23083
