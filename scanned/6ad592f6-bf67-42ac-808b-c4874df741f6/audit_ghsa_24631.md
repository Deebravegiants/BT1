# [H] Potentially compromised builds 

## Summary
Severity: High
Advisory: GHSA-rfj2-4g26-7jw5
CVE: CVE-2019-10249
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rfj2-4g26-7jw5
Type: github-advisory

## Affected
- Maven: `org.eclipse.xtext:org.eclipse.xtext` — affected >=0 <2.18.0
- Maven: `org.eclipse.xtend:org.eclipse.xtend.core` — affected >=0 <2.18.0

## Details
All Xtext & Xtend versions prior to 2.18.0 were built using HTTP instead of HTTPS file transfer and thus the built artifacts may have been compromised.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10249
- https://github.com/eclipse/xtext-xtend/issues/759
- https://github.com/eclipse/xtext-xtend/commit/169de2cecc50ed9bf81c3cdc496ad8a799bdf17b
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=546996
