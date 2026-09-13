# [H] xxl-job sensitive data exposure

## Summary
Severity: High
Advisory: GHSA-m5q9-488r-4rmp
CVE: CVE-2020-23811
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m5q9-488r-4rmp
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job` — affected >=0

## Details
xxl-job 2.2.0 allows Information Disclosure of username, model, and password via job/admin/controller/UserController.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23811
- https://github.com/xuxueli/xxl-job
