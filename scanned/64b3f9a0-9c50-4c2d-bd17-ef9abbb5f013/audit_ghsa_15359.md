# [M] Apache Answer: The link for resetting user password is not Single-Use

## Summary
Severity: Medium
Advisory: GHSA-v3x9-wrq5-868j
CVE: CVE-2024-41888
CWE: CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-v3x9-wrq5-868j
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.3.6

## Details
Missing Release of Resource after Effective Lifetime vulnerability in Apache Answer.

This issue affects Apache Answer: through 1.3.5.

The password reset link remains valid within its expiration period even after it has been used. This could potentially lead to the link being misused or hijacked.
Users are recommended to upgrade to version 1.3.6, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41888
- https://github.com/apache/incubator-answer/commit/2820efc454f5808974dce0aa99aac106be3f727b
- https://lists.apache.org/thread/jbs1j2o9rqm5sc19jyk3jcfvkmfkmyf4
- github.com/apache/incubator-answer
- http://www.openwall.com/lists/oss-security/2024/08/09/5
