# [H] ALPINE-CVE-2017-15650

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-15650
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15650
Type: osv

## Affected
- Alpine:v3.2: `musl` — affected >=0 <1.1.11-r5
- Alpine:v3.3: `musl` — affected >=0 <1.1.12-r8
- Alpine:v3.4: `musl` — affected >=0 <1.1.14-r16
- Alpine:v3.5: `musl` — affected >=0 <1.1.15-r8
- Alpine:v3.6: `musl` — affected >=0 <1.1.16-r14

## Details
musl libc before 1.1.17 has a buffer overflow via crafted DNS replies because dns_parse_callback in network/lookup_name.c does not restrict the number of addresses, and thus an attacker can provide an unexpected number by sending A records in a reply to an AAAA query.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15650
