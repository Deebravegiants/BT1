# [H] CVE-2021-29495

## Summary
Severity: High
Advisory: CVE-2021-29495
Aliases: GHSA-9vqv-2jj9-7mqr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-05-07
Source: https://osv.dev/vulnerability/CVE-2021-29495
Type: osv

## Details
Nim is a statically typed compiled systems programming language. In Nim standard library before 1.4.2, httpClient SSL/TLS certificate verification was disabled by default. Users can upgrade to version 1.4.2 to receive a patch or, as a workaround, set "verifyMode = CVerifyPeer" as documented.

## References
- https://github.com/nim-lang/security/security/advisories/GHSA-9vqv-2jj9-7mqr
