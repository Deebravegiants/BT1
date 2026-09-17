# [H] ALPINE-CVE-2023-2911

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-2911
Ecosystem: Alpine:v3.15
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-2911
Type: osv

## Affected
- Alpine:v3.15: `bind` — affected >=9.16.33 <9.16.42-r0

## Details
If the `recursive-clients` quota is reached on a BIND 9 resolver configured with both `stale-answer-enable yes;` and `stale-answer-client-timeout 0;`, a sequence of serve-stale-related lookups could cause `named` to loop and terminate unexpectedly due to a stack overflow.
This issue affects BIND 9 versions 9.16.33 through 9.16.41, 9.18.7 through 9.18.15, 9.16.33-S1 through 9.16.41-S1, and 9.18.11-S1 through 9.18.15-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-2911
