# [H] xuxueli xxl-job Cross-Site Request Forgery Vulnerability

## Summary
Severity: High
Advisory: GHSA-jp5r-4x9q-4vcf
CVE: CVE-2020-24922
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-jp5r-4x9q-4vcf
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job` — affected >=0

## Details
Cross Site Request Forgery (CSRF) vulnerability in `xxl-job-admin/user/add` in xuxueli xxl-job version 2.2.0 allows remote attackers to execute arbitrary code and esclate privileges via crafted .html file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24922
- https://github.com/xuxueli/xxl-job/issues/1921
- https://github.com/xuxueli/xxl-job
