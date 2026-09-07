# [M] Cross-site Scripting in Pivotal Spring Batch Admin

## Summary
Severity: Medium
Advisory: GHSA-4cj8-779h-r25h
CVE: CVE-2018-1229
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4cj8-779h-r25h
Type: github-advisory

## Affected
- Maven: `org.springframework.batch:spring-batch-admin-manager` — affected >=0

## Details
Pivotal Spring Batch Admin, all versions, contains a stored XSS vulnerability in the file upload feature. An unauthenticated malicious user with network access to Spring Batch Admin could store an arbitrary web script that would be executed by other users. This issue has not been patched because Spring Batch Admin has reached end of life.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1229
- https://pivotal.io/security/cve-2018-1229
- http://www.securityfocus.com/bid/103462
