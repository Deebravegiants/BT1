# [H] CVE-2017-1000107

## Summary
Severity: High
Advisory: CVE-2017-1000107
Aliases: GHSA-h7rx-r733-7x7r
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-1000107
Type: osv

## Details
Script Security Plugin did not apply sandboxing restrictions to constructor invocations via positional arguments list, super constructor invocations, method references, and type coercion expressions. This could be used to invoke arbitrary constructors and methods, bypassing sandbox protection.

## References
- https://jenkins.io/security/advisory/2017-08-07/
