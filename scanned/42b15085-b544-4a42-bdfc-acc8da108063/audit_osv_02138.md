# [H] ALPINE-CVE-2021-27291

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27291
Ecosystem: Alpine:v3.11, Alpine:v3.12
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27291
Type: osv

## Affected
- Alpine:v3.11: `py3-pygments` — affected >=0 <2.5.2-r1
- Alpine:v3.12: `py3-pygments` — affected >=0 <2.6.1-r1

## Details
In pygments 1.1+, fixed in 2.7.4, the lexers used to parse programming languages rely heavily on regular expressions. Some of the regular expressions have exponential or cubic worst-case complexity and are vulnerable to ReDoS. By crafting malicious input, an attacker can cause a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27291
