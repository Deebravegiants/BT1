# [M] ALPINE-CVE-2026-4891

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-4891
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4891
Type: osv

## Affected
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.92_p2-r0

## Details
A heap-based out-of-bounds read vulnerability in the DNSSEC validation of dnsmasq allows remote attackers to cause a denial of service via a crafted DNS packet.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4891
