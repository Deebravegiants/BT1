# [M] MyBB: Security Question insufficient validation

## Summary
Severity: Medium
Advisory: CVE-2026-46482
Aliases: GHSA-v2h7-4jp7-j6hh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-46482
Type: osv

## Details
### Impact
The registration component does not validate the text-based _Security Question_ CAPTCHA correctly, allowing attackers to bypass the challenge via a specially crafted value.


[CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N](https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)

### Details
The public _Registration_ workflow ([`member.php?action=do_register`](https://github.com/mybb/mybb/blob/mybb_1839/member.php#L262-L307)) accepts a hidden field `question_id` — expected to match the question session identifier (`mybb_questionsessions.sid`) — and validates the challenge answer without a fail-closed fallback for invalid identifiers. If the value is blank, forged, or expired, the request continues without a question-related error.

### Patches
MyBB 1.8.(...) resolves this issue with the following changes:

- Commit: https://github.com/mybb/mybb/commit/
  - `.patch`: https://github.com/mybb/mybb/commit/.patch

### References
- Release Notes: https://mybb.com/versions/1.8.(...)/

### For more information
Go to [mybb.com/security](https://mybb.com/security/) to report possible security concerns or to learn more about security research at MyBB.

### Contact
The security team can be reached at [security@mybb.com](mailto:security@mybb.com).

## References
- https://github.com/mybb/mybb/releases/tag/mybb_1840
- https://mybb.com/versions/1.8.40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46482.json
- https://github.com/mybb/mybb/security/advisories/GHSA-v2h7-4jp7-j6hh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46482
- https://github.com/mybb/mybb/commit/bd2a3447939d3084a5926dd66ece04649e0e0d60
