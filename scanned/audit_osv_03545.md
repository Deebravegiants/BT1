# [M] ALPINE-CVE-2026-27856

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-27856
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27856
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=3.0.0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=3.0.0 <2.4.3-r0

## Details
Doveadm credentials are verified using direct comparison which is susceptible to timing oracle attack. An attacker can use this to determine the configured credentials. Figuring out the credential will lead into full access to the affected component. Limit access to the doveadm http service port, install fixed version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27856
