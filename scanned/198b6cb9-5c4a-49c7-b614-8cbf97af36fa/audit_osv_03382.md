# [M] ALPINE-CVE-2025-68276

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-68276
Ecosystem: Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-68276
Type: osv

## Affected
- Alpine:v3.24: `avahi` — affected >=0 <0.8-r25

## Details
Avahi is a system which facilitates service discovery on a local network via the mDNS/DNS-SD protocol suite. In 0.9-rc2 and earlier, an unprivileged local users can crash avahi-daemon (with wide-area disabled) by creating record browsers with the AVAHI_LOOKUP_USE_WIDE_AREA flag set via D-Bus. This can be done by either calling
the RecordBrowserNew method directly or creating hostname/address/service resolvers/browsers that create those browsers internally themselves.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-68276
