# [M] Apache Answer: The link to reset the user's password will remain valid after sending a new link

## Summary
Severity: Medium
Advisory: GHSA-gvpv-r32v-9737
CVE: CVE-2024-41890
CWE: CWE-772
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-gvpv-r32v-9737
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.3.6

## Details
Missing Release of Resource after Effective Lifetime vulnerability in Apache Answer.

This issue affects Apache Answer: through 1.3.5.

User sends multiple password reset emails, each containing a valid link. Within the link's validity period, this could potentially lead to the link being misused or hijacked.
Users are recommended to upgrade to version 1.3.6, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41890
- https://github.com/apache/incubator-answer/commit/2820efc454f5808974dce0aa99aac106be3f727b
- https://lists.apache.org/thread/j7c080xj31x8rvz1pyk2h47rdd9pwbv9
- github.com/apache/incubator-answer
- http://www.openwall.com/lists/oss-security/2024/08/09/4
