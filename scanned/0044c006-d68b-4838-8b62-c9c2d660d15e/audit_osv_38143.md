# [M] Apache Answer: Unlisted Questions Accessible via Direct API Access

## Summary
Severity: Medium
Advisory: CVE-2026-34905
Aliases: GHSA-85r2-pvg8-89r9, GO-2026-6152
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-34905
Type: osv

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.0.

The unlisted question feature did not enforce access restrictions on direct API endpoints, allowing authenticated users to discover and access unlisted questions, their answers, comments, and revision history.
Users are recommended to upgrade to version 2.0.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/09/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34905.json
- https://lists.apache.org/thread/khxoft96sptr2kh0cpzgw7f6qwv0ltcf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34905
