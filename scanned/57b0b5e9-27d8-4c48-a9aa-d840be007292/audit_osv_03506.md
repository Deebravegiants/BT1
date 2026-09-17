# [H] ALPINE-CVE-2026-2291

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-2291
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-2291
Type: osv

## Affected
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.92_p2-r0

## Details
dnsmasqs extract_name() function can be abused to cause a heap buffer overflow, allowing an attacker to inject false DNS cache entries, which could result in DNS lookups to redirect to an attacker-controlled IP address, or to cause a DoS.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-2291
