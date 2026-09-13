# [M] ALPINE-CVE-2025-59031

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-59031
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-59031
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=3.0.0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=3.0.0 <2.4.3-r0

## Details
Dovecot has provided a script to use for attachment to text conversion. This script unsafely handles zip-style attachments. Attacker can use specially crafted OOXML documents to cause unintended files on the system to be indexed and subsequently ending up in FTS indexes. Do not use the provided script, instead, use something else like FTS tika. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-59031
