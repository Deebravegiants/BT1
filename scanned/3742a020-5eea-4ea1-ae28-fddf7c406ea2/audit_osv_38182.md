# [H] Apache Fineract: SQL injection in runreports endpoint

## Summary
Severity: High
Advisory: CVE-2026-35152
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-35152
Type: osv

## Details
A SQL Injection vulnerability exists in Apache Fineract's Report Execution API (runreports endpoint) in versions up to and including 1.14.0. Report parameter values are incorporated into the generated SQL query without sufficient validation, allowing an authenticated user with permission to run reports to inject arbitrary SQL via crafted parameter values. This can be leveraged to perform unauthorized access to data beyond what the report was designed to expose. Users are recommended to upgrade to a version containing the fix.

## References
- http://www.openwall.com/lists/oss-security/2026/07/15/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35152.json
- https://lists.apache.org/thread/658yddn0bpxqw2hpxnyk3vqd05bkchg9
- https://lists.apache.org/thread/d3bzcwsbywz7wg9zxvtlkvgmffqjyfn0
- https://nvd.nist.gov/vuln/detail/CVE-2026-35152
- https://github.com/apache/fineract/pull/5980
