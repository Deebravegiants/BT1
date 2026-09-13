# [C] Quest Bot: Untrusted pull request code can be built and deployed by privileged `workflow_run` deployment.

## Summary
Severity: Critical
Advisory: CVE-2026-47172
Aliases: GHSA-9qf3-c86c-j346
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-47172
Type: osv

## Details
Quest Bot is an opensource modern Discord Bot built for moderation, utilities and support. Prior to version 1.0.3, the repository has a privileged deploy workflow that runs after the unprivileged build workflow completes. The build workflow runs on pull requests, and the deploy workflow checks out the triggering workflow’s head_sha, builds that code into a Docker image, pushes it as latest, and triggers production deployment. If an attacker can open a pull request from a branch named main, the deploy workflow condition can treat the PR build as deployable and build the attacker-controlled commit in a privileged deployment context. This can result in malicious container deployment and production bot compromise. This issue has been patched in version 1.0.3.

## References
- https://github.com/duck-organization/questbot/releases/tag/questbot-v1.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47172.json
- https://github.com/duck-organization/questbot/security/advisories/GHSA-9qf3-c86c-j346
- https://nvd.nist.gov/vuln/detail/CVE-2026-47172
