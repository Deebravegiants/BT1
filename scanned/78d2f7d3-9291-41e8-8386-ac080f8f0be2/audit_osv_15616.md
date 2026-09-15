# [H] CVE-2019-17633

## Summary
Severity: High
Advisory: CVE-2019-17633
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-19
Source: https://osv.dev/vulnerability/CVE-2019-17633
Type: osv

## Details
For Eclipse Che versions 6.16 to 7.3.0, with both authentication and TLS disabled, visiting a malicious web site could trigger the start of an arbitrary Che workspace. Che with no authentication and no TLS is not usually deployed on a public network but is often used for local installations (e.g. on personal laptops). In that case, even if the Che API is not exposed externally, some javascript running in the local browser is able to send requests to it.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=551596
