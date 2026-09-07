# [M] Stored Cross Site Scripting in beetl-bbs

## Summary
Severity: Medium
Advisory: GHSA-32q4-86g8-6637
CVE: CVE-2024-22491
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-16
Source: https://github.com/advisories/GHSA-32q4-86g8-6637
Type: github-advisory

## Affected
- Maven: `com.ibeetl:beetl` — affected >=0

## Details
A Stored Cross Site Scripting (XSS) vulnerability in beetl-bbs 2.0 allows attackers to run arbitrary code via the post/save content parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22491
- https://github.com/cui2shark/security/blob/main/A%20stored%20cross-site%20scripting%20%28XSS%29%20vulnerability%20was%20discovered%20in%20beetl-bbs%20post%20save.md
