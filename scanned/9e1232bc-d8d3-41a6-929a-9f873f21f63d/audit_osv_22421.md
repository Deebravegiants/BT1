# [M] No verification of commits origin in github-action-merge-dependabot

## Summary
Severity: Medium
Advisory: CVE-2022-29220
Aliases: GHSA-v5vr-h3xq-8v6w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-05-31
Source: https://osv.dev/vulnerability/CVE-2022-29220
Type: osv

## Details
github-action-merge-dependabot is an action that automatically approves and merges dependabot pull requests (PRs). Prior to version 3.2.0, github-action-merge-dependabot does not check if a commit created by dependabot is verified with the proper GPG key. There is just a check if the actor is set to `dependabot[bot]` to determine if the PR is a legit PR. Theoretically, an owner of a seemingly valid and legit action in the pipeline can check if the PR is created by dependabot and if their own action has enough permissions to modify the PR in the pipeline. If so, they can modify the PR by adding a second seemingly valid and legit commit to the PR, as they can set arbitrarily the username and email in for commits in git. Because the bot only checks if the actor is valid, it would pass the malicious changes through and merge the PR automatically, without getting noticed by project maintainers. It would probably not be possible to determine where the malicious commit came from, as it would only say `dependabot[bot]` and the corresponding email-address. Version 3.2.0 contains a patch for this issue.

## References
- https://hackerone.com/bugs?report_id=1564530
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29220.json
- https://github.com/fastify/github-action-merge-dependabot/security/advisories/GHSA-v5vr-h3xq-8v6w
- https://nvd.nist.gov/vuln/detail/CVE-2022-29220
- https://github.com/fastify/github-action-merge-dependabot/commit/309f39539c5d918d8a47075587aa8720a9c127f7
