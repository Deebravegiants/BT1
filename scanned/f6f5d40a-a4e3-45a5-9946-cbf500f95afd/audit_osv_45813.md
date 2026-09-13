# [M] JLSEC-2026-36

## Summary
Severity: Medium
Advisory: JLSEC-2026-36
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-36
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.1.0+0

## Details
Odyssey passes to client unencrypted bytes from man-in-the-middle When Odyssey storage is configured to use the PostgreSQL server using 'trust' authentication with a 'clientcert' requirement or to use 'cert' authentication, a man-in-the-middle attacker can inject false responses to the client's first few queries. Despite the use of SSL certificate verification and encryption, Odyssey will pass these results to client as if they originated from valid server. This is similar to CVE-2021-23222 for PostgreSQL.

## References
- https://github.com/yandex/odyssey/issues/377%2C
- https://www.postgresql.org/support/security/CVE-2021-23222/
