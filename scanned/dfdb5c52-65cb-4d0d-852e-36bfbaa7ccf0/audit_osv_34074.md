# [C] dedupe is vulnerable to secret exfiltration via `issue_comment`

## Summary
Severity: Critical
Advisory: CVE-2025-54430
Aliases: GHSA-wrg3-xqw8-m85p
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2025-54430
Type: osv

## Details
dedupe is a python library that uses machine learning to perform fuzzy matching, deduplication and entity resolution quickly on structured data. Before commit 3f61e79, a critical severity vulnerability has been identified within the .github/workflows/benchmark-bot.yml workflow, where a issue_comment can be triggered using the @benchmark body. This workflow is susceptible to exploitation as it checkout the ${{ github.event.issue.number }}, which correspond to the branch of the PR manipulated by potentially malicious actors, and where untrusted code may be executed. Running untrusted code may lead to the exfiltration of GITHUB_TOKEN, which in this workflow has write permissions on most of the scopes - in particular the contents one - and could lead to potential repository takeover. This is fixed by commit 3f61e79.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54430.json
- https://github.com/dedupeio/dedupe/security/advisories/GHSA-wrg3-xqw8-m85p
- https://nvd.nist.gov/vuln/detail/CVE-2025-54430
- https://github.com/dedupeio/dedupe/commit/3f61e79102910bd355e920a2df7e44c14c9cb247
