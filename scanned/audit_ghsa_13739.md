# [M] xxl-job-admin vulnerable to Insecure Permissions

## Summary
Severity: Medium
Advisory: GHSA-3w8r-3jh9-89v9
CVE: CVE-2023-48087
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-3w8r-3jh9-89v9
Type: github-advisory

## Affected
- Maven: `com.xuxueli:xxl-job-admin` — affected >=0

## Details
xxl-job-admin 2.4.0 is vulnerable to Insecure Permissions via /xxl-job-admin/joblog/clearLog and /xxl-job-admin/joblog/logDetailCat.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48087
- https://github.com/xuxueli/xxl-job/issues/3330
- https://github.com/xuxueli/xxl-job
