# [H] ALPINE-CVE-2019-12625

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12625
Ecosystem: Alpine:v3.12, Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12625
Type: osv

## Affected
- Alpine:v3.12: `clamav` — affected >=0 <0.101.4-r0
- Alpine:v3.13: `clamav` — affected >=0 <0.101.4-r0

## Details
ClamAV versions prior to 0.101.3 are susceptible to a zip bomb vulnerability where an unauthenticated attacker can cause a denial of service condition by sending crafted messages to an affected system.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12625
