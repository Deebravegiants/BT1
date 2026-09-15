# [M] CVE-2021-33586

## Summary
Severity: Medium
Advisory: CVE-2021-33586
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-33586
Type: osv

## Details
InspIRCd 3.8.0 through 3.9.x before 3.10.0 allows any user (able to connect to the server) to access recently deallocated memory, aka the "malformed PONG" issue.

## References
- https://security.gentoo.org/glsa/202107-22
- https://docs.inspircd.org/security/2021-01/
- https://github.com/inspircd/inspircd/commit/4350a11c663b0d75f8119743bffb7736d87abd4d
