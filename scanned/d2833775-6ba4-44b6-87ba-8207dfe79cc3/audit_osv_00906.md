# [H] ALPINE-CVE-2018-10915

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10915
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10915
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.11: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.12: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.13: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.14: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.5: `postgresql` — affected >=9.3.0 <9.6.10-r0
- Alpine:v3.6: `postgresql` — affected >=9.3.0 <9.6.10-r0
- Alpine:v3.7: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.8: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.9: `postgresql` — affected >=9.3.0 <10.5-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <10.5-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <10.5-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <10.5-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <10.5-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <10.5-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <10.5-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <10.5-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <10.5-r0

## Details
A vulnerability was found in libpq, the default PostgreSQL client library where libpq failed to properly reset its internal state between connections. If an affected version of libpq was used with "host" or "hostaddr" connection parameters from untrusted input, attackers could bypass client-side connection security features, obtain access to higher privileged connections or potentially cause other impact through SQL injection, by causing the PQescape() functions to malfunction. Postgresql versions before 10.5, 9.6.10, 9.5.14, 9.4.19, and 9.3.24 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10915
