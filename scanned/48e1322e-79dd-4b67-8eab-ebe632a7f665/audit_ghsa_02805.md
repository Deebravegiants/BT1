# [C] Expression injection in AviatorScript

## Summary
Severity: Critical
Advisory: GHSA-xpv2-8ppj-79hh
CVE: CVE-2021-41862
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-04
Source: https://github.com/advisories/GHSA-xpv2-8ppj-79hh
Type: github-advisory

## Affected
- Maven: `com.googlecode.aviator:aviator` — affected >=5.2.1

## Details
AviatorScript through 5.2.7 allows code execution via an expression that is encoded with Byte Code Engineering Library (BCEL).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41862
- https://github.com/killme2008/aviatorscript/issues/421
- https://github.com/killme2008/aviatorscript
