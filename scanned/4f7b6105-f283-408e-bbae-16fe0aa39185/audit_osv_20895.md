# [C] CVE-2021-38167

## Summary
Severity: Critical
Advisory: CVE-2021-38167
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/CVE-2021-38167
Type: osv

## Details
Roxy-WI through 5.2.2.0 allows SQL Injection via check_login. An unauthenticated attacker can extract a valid uuid to bypass authentication.

## References
- https://github.com/hap-wi/roxy-wi/issues/285
