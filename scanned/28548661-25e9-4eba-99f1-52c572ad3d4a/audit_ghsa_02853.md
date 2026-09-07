# [M] Cross-site Scripting in XXL-JOB

## Summary
Severity: Medium
Advisory: GHSA-wc73-w5r9-x9pc
CVE: CVE-2020-29204
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-wc73-w5r9-x9pc
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job-core` — affected >=0 <2.3.0

## Details
XXL-JOB 2.2.0 allows Stored XSS (in Add User) to bypass the 20-character limit via xxl-job-admin/src/main/java/com/xxl/job/admin/controller/UserController.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29204
- https://github.com/xuxueli/xxl-job/issues/2083
- https://github.com/xuxueli/xxl-job/commit/227628567354d3c156951009d683c6fec3006e0e
- https://github.com/xuxueli/xxl-job
