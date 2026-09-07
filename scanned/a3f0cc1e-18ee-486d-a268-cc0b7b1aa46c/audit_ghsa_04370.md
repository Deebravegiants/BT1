# [M] Apache Answer vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-6qwm-5fm9-cvjx
CVE: CVE-2026-34033
CWE: CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-6qwm-5fm9-cvjx
Type: github-advisory

## Affected
- Go: `github.com/apache/incubator-answer` — affected >=0 <1.7.2-0.20260509080709-d1a4092c61cc

## Details
Improper Neutralization of Script-Related HTML Tags in a Web Page (Basic XSS) vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.0.

User-supplied content was included in notification emails without proper escaping, allowing authenticated users to inject arbitrary HTML into emails sent to other users.
Users are recommended to upgrade to version 2.0.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34033
- https://github.com/apache/answer/commit/d1a4092c61ccd41988d1033fce47eb513adb433e
- https://github.com/apache/answer
- https://github.com/apache/answer/releases/tag/v2.0.1
- https://lists.apache.org/thread/wrfd9blbfotfg479jr8vlwfx6pwr9sgj
- http://www.openwall.com/lists/oss-security/2026/06/09/3
