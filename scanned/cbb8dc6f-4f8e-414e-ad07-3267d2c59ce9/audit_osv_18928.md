# [H] CVE-2020-5207

## Summary
Severity: High
Advisory: CVE-2020-5207
Aliases: GHSA-xrr9-rh8p-433v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-01-27
Source: https://osv.dev/vulnerability/CVE-2020-5207
Type: osv

## Details
In Ktor before 1.3.0, request smuggling is possible when running behind a proxy that doesn't handle Content-Length and Transfer-Encoding properly or doesn't handle \n as a headers separator.

## References
- https://github.com/ktorio/ktor/security/advisories/GHSA-xrr9-rh8p-433v
- https://github.com/ktorio/ktor/pull/1547
