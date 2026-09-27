# [H] ALPINE-CVE-2026-11622

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11622
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11622
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
A DNSSEC validating resolver that is under a random subdomain attack against a DNSSEC-signed zone can suffer from runaway memory usage. The attacker needs to be able to send queries faster than the resolver can perform validation. The increased memory usage can be orders of magnitude beyond the limit configured in the `max-cache-size` parameter.
This issue affects BIND 9 versions 9.11.0 through 9.18.50, 9.20.0 through 9.20.24, 9.21.0 through 9.21.23, 9.11.3-S1 through 9.18.50-S1, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11622
