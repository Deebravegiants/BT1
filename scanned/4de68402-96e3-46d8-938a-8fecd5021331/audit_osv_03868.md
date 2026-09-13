# [M] ALPINE-CVE-2026-58042

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-58042
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-58042
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.23.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <24.18.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.18.1-r0

## Details
A flaw in Node.js can cause dns.resolveAny() Aborts the Node.js Process When a DNS Response Contains More Than 256 A Records.

Repeated triggering of this condition can lead to denial of service.

This vulnerability affects Node.js **26.x**, **24.x**, and **22.x**.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-58042
