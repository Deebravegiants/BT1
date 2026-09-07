# [M] Cross-site Scripting in jeecg-boot

## Summary
Severity: Medium
Advisory: GHSA-q448-6c3m-cxmj
CVE: CVE-2021-44585
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-q448-6c3m-cxmj
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-base` — affected >=0 <3.1.0
- Maven: `org.jeecgframework.boot:jeecg-boot-base-core` — affected >=0 <3.1.0

## Details
jeecg-boot is a code generator. A Cross Site Scripting (XSS) vulnerabilitiy exists in jeecg-boot 3.0 in /jeecg-boot/jmreport/view with a mouseover event.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44585
- https://github.com/jeecgboot/jeecg-boot/issues/3223
- https://github.com/jeecgboot/jeecg-boot/commit/dbba190980fe44ab5377703dc1a9487806ee2a91
- https://github.com/jeecgboot/jeecg-boot
