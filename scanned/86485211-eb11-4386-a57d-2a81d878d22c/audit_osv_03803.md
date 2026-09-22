# [H] ALPINE-CVE-2026-5172

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-5172
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5172
Type: osv

## Affected
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.92_p2-r0

## Details
A buffer overflow in dnsmasq’s extract_addresses() function allows an attacker to trigger a heap out-of-bounds read and crash by exploiting a malformed DNS response, enabling extract_name() to advance the pointer past the record’s end.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5172
