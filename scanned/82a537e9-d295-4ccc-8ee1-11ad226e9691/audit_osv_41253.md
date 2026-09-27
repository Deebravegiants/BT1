# [M] LobeChat < 2.2.10-canary.15 - Regular Expression Denial of Service in GitHub Skill Import

## Summary
Severity: Medium
Advisory: CVE-2026-58578
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58578
Type: osv

## Details
LobeChat before version 2.2.10-canary.15 contains a regular expression denial of service (ReDoS) vulnerability that allows authenticated attackers to block the Node.js event loop by supplying a catastrophic-backtracking pattern in a GitHub repository URL path during skill import. Attackers can craft a malicious basePath value containing unescaped regex metacharacters such as catastrophic-backtracking patterns, which are injected into a dynamically constructed regular expression in the findSkillMd function and executed synchronously against archive entries, denying service to all concurrent users for tens of seconds per request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58578.json
- https://github.com/lobehub/lobehub/releases/tag/v2.2.10-canary.15
- https://nvd.nist.gov/vuln/detail/CVE-2026-58578
- https://www.vulncheck.com/advisories/lobechat-canary-15-regular-expression-denial-of-service-in-github-skill-import
- https://github.com/lobehub/lobehub/pull/16548
- https://github.com/lobehub/lobehub/commit/349bbe326eb8635d6d9c6a96d12702681ae3a84a
- https://github.com/lobehub/lobehub
- https://github.com/lobehub/lobehub/issues/16494
