# [M] ALPINE-CVE-2025-68468

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-68468
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-68468
Type: osv

## Affected
- Alpine:v3.24: `avahi` — affected >=0 <0.8-r25

## Details
Avahi is a system which facilitates service discovery on a local network via the mDNS/DNS-SD protocol suite. In 0.9-rc2 and earlier, avahi-daemon can be crashed by sending unsolicited announcements containing CNAME resource records pointing it to resource records with short TTLs. As soon as they expire avahi-daemon crashes.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-68468
