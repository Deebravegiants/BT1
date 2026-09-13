# [C] Woodpecker < 3.15.0 - GitLab Approval Gate Bypass via Spoofable Commit Author Name

## Summary
Severity: Critical
Advisory: CVE-2026-58370
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58370
Type: osv

## Details
Woodpecker before 3.15.0 matches the ApprovalAllowedUsers bypass list against pipeline.Author. For the GitLab forge driver, pipeline.Author is populated from the git commit author name (commit.author.name) carried in the webhook payload, which is attacker-controlled and not verified by GitLab. A user who can open a merge request from a fork can set the commit author name to match an entry in ApprovalAllowedUsers, causing needsApproval to return false so the pipeline runs without the required approval. This defeats the fork-approval security boundary and allows execution of attacker-controlled pipeline steps on a Woodpecker agent and exfiltration of CI secrets exposed to the run. Other built-in forge drivers (Gitea, Forgejo, GitHub, Bitbucket) derive pipeline.Author from the forge-validated sender/actor identity and are not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58370.json
- https://github.com/woodpecker-ci/woodpecker/releases/tag/v3.15.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-58370
- https://www.vulncheck.com/advisories/woodpecker-gitlab-approval-gate-bypass-via-spoofable-commit-author-name
- https://github.com/woodpecker-ci/woodpecker/pull/6653
- https://github.com/woodpecker-ci/woodpecker/commit/98faae778c953678944996c89ed99307d2f16a3d
- https://github.com/woodpecker-ci/woodpecker
