# [M] ALPINE-CVE-2026-50045

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-50045
Ecosystem: Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-50045
Type: osv

## Affected
- Alpine:v3.24: `unbound` — affected >=1.22.0 <1.25.2-r0

## Details
In NLnet Labs Unbound 1.22.0 up to and including 1.25.1, a single client query for a deeply nested name under a DNSSEC-signed parent can cause Unbound to send more upstream packets per client query than the configured 'max-global-quota'. This effectively bypasses a security configuration that limits upstream amplification traffic.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-50045
