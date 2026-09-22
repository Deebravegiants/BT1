# [H] ALPINE-CVE-2019-11707

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-11707
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11707
Type: osv

## Affected
- Alpine:v3.10: `mozjs60` — affected >=0 <60.7.2-r0
- Alpine:v3.11: `mozjs60` — affected >=0 <60.7.2-r0
- Alpine:v3.12: `mozjs60` — affected >=0 <60.7.2-r0

## Details
A type confusion vulnerability can occur when manipulating JavaScript objects due to issues in Array.pop. This can allow for an exploitable crash. We are aware of targeted attacks in the wild abusing this flaw. This vulnerability affects Firefox ESR < 60.7.1, Firefox < 67.0.3, and Thunderbird < 60.7.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11707
