# [M] Apache Answer Race Condition vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9q24-hwmc-797x
CVE: CVE-2024-26578
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-9q24-hwmc-797x
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.2.5

## Details
Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition') vulnerability in Apache Answer. This issue affects Apache Answer through 1.2.1.

Repeated submission during registration resulted in the registration of the same user. When users register, if they rapidly submit multiple registrations using scripts, it can result in the creation of multiple user accounts simultaneously with the same name.

Users are recommended to upgrade to version 1.2.5, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26578
- https://github.com/apache/incubator-answer
- https://lists.apache.org/thread/ko0ksnznt2484lxt0zts2ygr82ldkhcb
- http://www.openwall.com/lists/oss-security/2024/02/22/3
