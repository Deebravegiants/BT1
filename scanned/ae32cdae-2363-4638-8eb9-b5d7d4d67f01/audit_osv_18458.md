# [H] CVE-2020-27793

## Summary
Severity: High
Advisory: CVE-2020-27793
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-19
Source: https://osv.dev/vulnerability/CVE-2020-27793
Type: osv

## Details
An off-by-one overflow flaw was found in radare2 due to mismatched array length in core_java.c. This could allow an attacker to cause a crash, and perform a denail of service attack.

## References
- https://github.com/radareorg/radare2/commit/ced0223c7a1b3b5344af315715cd28fe7c0d9ebc
- https://github.com/radareorg/radare2/issues/16304
