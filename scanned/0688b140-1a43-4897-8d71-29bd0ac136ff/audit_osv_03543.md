# [H] ALPINE-CVE-2026-27852

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-27852
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27852
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that can send mail to a user can craft a message whose headers contain a very large number of email addresses or MIME parameters, which causes excessive memory usage when the message is later parsed. The message is still delivered, but reading it over IMAP can exhaust the memory limit of the process and terminate it, causing denial of service for the affected user. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27852
