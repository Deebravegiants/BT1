# [H] Postorius is vulnerable to XSS

## Summary
Severity: High
Advisory: GHSA-r7c9-7pjq-hmm8
CVE: CVE-2026-44742
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-r7c9-7pjq-hmm8
Type: github-advisory

## Affected
- PyPI: `postorius` — affected >=0

## Details
Postorius through 1.3.13 does not escape HTML in the message subject when rendering it in the Held messages pop-up, as exploited in the wild in May 2026.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44742
- https://gitlab.com/mailman/postorius
- https://gitlab.com/mailman/postorius/-/commit/c4706abd05ba6bcf472fc674b160d3a9d6a4868b
- https://gitlab.com/mailman/postorius/-/issues/620
- https://gitlab.com/mailman/postorius/-/merge_requests/972
- https://www.openwall.com/lists/oss-security/2026/05/07/3
