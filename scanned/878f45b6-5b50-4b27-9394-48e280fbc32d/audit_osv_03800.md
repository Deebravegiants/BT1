# [M] ALPINE-CVE-2026-50248

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-50248
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-50248
Type: osv

## Affected
- Alpine:v3.24: `unbound` — affected >=1.7.0 <1.25.2-r0

## Details
In NLnet Labs Unbound 1.7.0 up to and including 1.25.1, when an auth/rpz zone has a configured primary hostname that resolves to BOGUS A/AAAA, it is still considered as a possible XFR endpoint. A malicious actor that can spoof the hostname's A/AAAA record (no valid RRSIG required) becomes the zone's XFR primary and can replaces the entire zone/the resolver's entire response policy.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-50248
