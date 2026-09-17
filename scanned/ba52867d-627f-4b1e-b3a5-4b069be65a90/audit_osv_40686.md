# [M] ToolJet GitHub Actions comment body shell injection exposes deployment secrets

## Summary
Severity: Medium
Advisory: CVE-2026-54344
Aliases: GHSA-4pm2-w6g5-28mm
CVSS: 4.7 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-54344
Type: osv

## Details
ToolJet is an open-source low-code platform for building internal tools. Prior to 3.20.180, ToolJet's render preview deployment workflow interpolates github.event.comment.body directly into a bash conditional in a run step, allowing any GitHub user who can comment on an open pull request with a deploy command to execute shell commands on the CI runner and exfiltrate deployment secrets. This issue is reported as fixed in version 3.20.180.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54344.json
- https://github.com/ToolJet/ToolJet/security/advisories/GHSA-4pm2-w6g5-28mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54344
