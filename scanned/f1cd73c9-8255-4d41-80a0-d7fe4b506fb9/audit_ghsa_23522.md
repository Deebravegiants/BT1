# [H] Spring Batch Admin vulnerable to Cross-site request forgery (CSRF) in the file upload functionality

## Summary
Severity: High
Advisory: GHSA-274r-p6v6-fhh4
CVE: CVE-2017-12881
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-274r-p6v6-fhh4
Type: github-advisory

## Affected
- Maven: `org.springframework.batch:spring-batch-admin-manager` — affected >=0 <1.3.0.RELEASE

## Details
Cross-site request forgery (CSRF) vulnerability in the Spring Batch Admin before 1.3.0 allows remote attackers to hijack the authentication of unspecified victims and submit arbitrary requests, such as exploiting the file upload vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12881
- https://github.com/spring-attic/spring-batch-admin
- http://www.openwall.com/lists/oss-security/2017/08/16/5
