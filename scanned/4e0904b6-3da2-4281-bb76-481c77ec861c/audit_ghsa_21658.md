# [M] Cross-site scripting in Apache Atlas

## Summary
Severity: Medium
Advisory: GHSA-h6xq-3h62-99qx
CVE: CVE-2020-13928
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-h6xq-3h62-99qx
Type: github-advisory

## Affected
- Maven: `org.apache.atlas:apache-atlas` — affected >=0 <2.1.0

## Details
Apache Atlas before 2.1.0 contain a XSS vulnerability. While saving search or rendering elements values are not sanitized correctly and because of that it triggers the XSS vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13928
- https://lists.apache.org/thread.html/ra468036f913be41b0c8fea74f91d53e273b0bfa838a4b140a5dcd463%40%3Cuser.atlas.apache.org%3E
- https://mvnrepository.com/artifact/org.apache.atlas/apache-atlas
