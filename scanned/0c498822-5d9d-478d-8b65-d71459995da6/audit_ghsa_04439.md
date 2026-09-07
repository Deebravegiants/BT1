# [H] Apache Answer: AdminToken not invalidated after admin deactivation

## Summary
Severity: High
Advisory: GHSA-4gw2-vg4x-7p29
CVE: CVE-2026-25700
CWE: CWE-1259
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-4gw2-vg4x-7p29
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <2.0.1
- Go: `github.com/apache/answer` — affected >=0 <2.0.1

## Details
Improper Restriction of Security Token Assignment vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.0.

Previously issued administrative tokens were not invalidated after an administrator account was suspended, deleted, or deactivated, allowing continued access to administrative APIs until the token expired.
Users are recommended to upgrade to version 2.0.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25700
- https://github.com/apache/answer
- https://github.com/apache/answer/releases/tag/v2.0.1
- https://lists.apache.org/thread/ftw52mlxknjm29vo1mnqovj53z2kh96y
- http://www.openwall.com/lists/oss-security/2026/06/10/10
