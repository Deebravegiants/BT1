# [M] ALPINE-CVE-2026-27859

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-27859
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27859
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=3.1.0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=3.1.0 <2.4.3-r0

## Details
A mail message containing excessive amount of RFC 2231 MIME parameters causes LMTP to use too much CPU. A suitably formatted mail message causes mail delivery process to consume large amounts of CPU time. Use MTA capabilities to limit RFC 2231 MIME parameters in mail messages, or upgrade to fixed version where the processing is limited. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27859
