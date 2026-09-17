# [M] ALPINE-CVE-2026-42006

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42006
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42006
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.4-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.4-r0

## Details
An attacker can cause uncontrolled memory usage with excessive bracing over IMAP. The fix in CVE-2026-27857 was incomplete, only blocking one way of doing this, so there was still another way left open. In particular, the fix was for closing braces, but you could still use open braces to bypass the limit. Using excessive bracing, attacker can cause memory usage up to configured memory limit. Install fixed version, or configure vsz_limit for imap process to low value. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42006
