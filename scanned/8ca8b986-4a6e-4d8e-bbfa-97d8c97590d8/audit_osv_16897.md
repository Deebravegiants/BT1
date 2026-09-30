# [M] CVE-2020-10577

## Summary
Severity: Medium
Advisory: CVE-2020-10577
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-03-14
Source: https://osv.dev/vulnerability/CVE-2020-10577
Type: osv

## Details
An issue was discovered in Janus through 0.9.1. janus.c has multiple concurrent threads that misuse the source property of a session, leading to a race condition when claiming sessions.

## References
- https://github.com/meetecho/janus-gateway/pull/1990
