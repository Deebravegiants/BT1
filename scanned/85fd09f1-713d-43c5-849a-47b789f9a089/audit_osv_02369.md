# [H] ALPINE-CVE-2022-0711

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-0711
Ecosystem: Alpine:v3.12, Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0711
Type: osv

## Affected
- Alpine:v3.12: `haproxy` — affected >=2.2.0 <2.2.21-r0
- Alpine:v3.13: `haproxy` — affected >=2.2.0 <2.2.21-r0

## Details
A flaw was found in the way HAProxy processed HTTP responses containing the "Set-Cookie2" header. This flaw could allow an attacker to send crafted HTTP response packets which lead to an infinite loop, eventually resulting in a denial of service condition. The highest threat from this vulnerability is availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0711
