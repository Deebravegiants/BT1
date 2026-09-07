# [M] NocoDB Vulnerable to Stored Cross-Site Scripting via Rich Text Cells

## Summary
Severity: Medium
Advisory: GHSA-wwp2-x4rj-j8rm
CVE: CVE-2026-28401
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-wwp2-x4rj-j8rm
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.3

## Details
### Summary
Rich text cell content rendered via `v-html` without sanitization, enabling stored XSS.

### Details
Rich text in `TextArea.vue` was parsed by markdown-it with `html: true` and injected via `v-html` without DOMPurify. A user with Editor role can inject arbitrary HTML that executes for all viewers.

### Impact
Stored XSS — malicious scripts execute for any user viewing the cell.

### Credit
This issue was discovered by an AI agent developed by the GitHub Security Lab and reviewed by GHSL team members [@p-](https://github.com/p-) (Peter Stockli) and [@m-y-mo](https://github.com/m-y-mo) (Man Yue Mo).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-wwp2-x4rj-j8rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-28401
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/0.301.3
