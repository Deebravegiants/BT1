# [H] Improper Restriction of XML External Entity Reference in PMD

## Summary
Severity: High
Advisory: GHSA-57qj-79gh-69w8
CVE: CVE-2019-7722
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-57qj-79gh-69w8
Type: github-advisory

## Affected
- Maven: `net.sourceforge.pmd:pmd-core` — affected >=0 <6.0.0

## Details
PMD 5.8.1 and earlier processes XML external entities in ruleset files it parses as part of the analysis process, allowing attackers tampering it (either by direct modification or MITM attacks when using remote rulesets) to perform information disclosure, denial of service, or request forgery attacks. (PMD 6.x is unaffected because of a 2017-09-15 change.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7722
- https://github.com/pmd/pmd/issues/1650
- https://github.com/pmd/pmd
