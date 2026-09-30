# [M] ALPINE-CVE-2024-23184

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-23184
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-23184
Type: osv

## Affected
- Alpine:v3.21: `dovecot` — affected >=0 <2.3.21.1-r0
- Alpine:v3.22: `dovecot` — affected >=0 <2.3.21.1-r0
- Alpine:v3.23: `dovecot` — affected >=0 <2.3.21.1-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.3.21.1-r0

## Details
Having a large number of address headers (From, To, Cc, Bcc, etc.) becomes excessively CPU intensive. With 100k header lines CPU usage is already 12 seconds, and in a production environment we observed 500k header lines taking 18 minutes to parse. Since this can be triggered by external actors sending emails to a victim, this is a security issue. An external attacker can send specially crafted messages that consume target system resources and cause outage. One can implement restrictions on address headers on MTA component preceding Dovecot. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-23184
