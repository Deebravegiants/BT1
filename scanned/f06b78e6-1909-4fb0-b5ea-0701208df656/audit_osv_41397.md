# [H] Apache Answer: Unauthorized disclosure of deleted or pending answer content

## Summary
Severity: High
Advisory: CVE-2026-60023
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-60023
Type: osv

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.1.

Deleted or pending answers could be retrieved by unauthorized users through the single-answer read path when the parent question remained visible, exposing answer content that should not have been accessible.
Users are recommended to upgrade to version 2.0.2, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60023.json
- https://lists.apache.org/thread/rq3ygd0j9cchkbmh99dqf8624s7r8y49
- https://nvd.nist.gov/vuln/detail/CVE-2026-60023
