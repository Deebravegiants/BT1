# [C] ALPINE-CVE-2026-42007

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-42007
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42007
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that has valid credentials can use a Sieve script with the editheader extension to trigger a use-after-free in the mail editing code, and to write memory contents beyond the intended buffer into the delivered mail. This causes memory leak and opportunity to do memory corruption during mail delivery, which can crash the delivery process and may allow execution of arbitrary code in the context of that process. Disable the Sieve editheader extension. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42007
