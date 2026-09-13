# [M] CVE-2019-16370

## Summary
Severity: Medium
Advisory: CVE-2019-16370
Aliases: GHSA-hhr2-f668-ff2w
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2019-16370
Type: osv

## Details
The PGP signing plugin in Gradle before 6.0 relies on the SHA-1 algorithm, which might allow an attacker to replace an artifact with a different one that has the same SHA-1 message digest, a related issue to CVE-2005-4900.

## References
- https://github.com/gradle/gradle/commit/425b2b7a50cd84106a77cdf1ab665c89c6b14d2f
- https://github.com/gradle/gradle/pull/10543
