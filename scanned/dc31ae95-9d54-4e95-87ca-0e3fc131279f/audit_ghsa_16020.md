# [M] Recursive repository cloning can leak authentication tokens to non-GitHub submodule hosts

## Summary
Severity: Medium
Advisory: GHSA-jwcm-9g39-pmcw
CVE: CVE-2024-53858
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-11-27
Source: https://github.com/advisories/GHSA-jwcm-9g39-pmcw
Type: github-advisory

## Affected
- Go: `github.com/cli/cli/v2` — affected >=0 <2.63.0

## Details
### Summary

A security vulnerability has been identified in the GitHub CLI that could leak authentication tokens when cloning repositories containing `git` submodules hosted outside of GitHub.com and ghe.com.

### Details

This vulnerability stems from several `gh` commands used to clone a repository with submodules from a non-GitHub host including `gh repo clone`, `gh repo fork`, `gh pr checkout`. These GitHub CLI commands invoke `git` with instructions to retrieve authentication tokens using the [`credential.helper`](https://git-scm.com/docs/gitcredentials) configuration variable for any host encountered.

Prior to `2.63.0`, hosts other than GitHub.com and ghe.com are treated as GitHub Enterprise Server hosts and have tokens sourced from the following environment variables before falling back to host-specific tokens stored within system-specific secured storage:

- `GITHUB_ENTERPRISE_TOKEN`
- `GH_ENTERPRISE_TOKEN`
- `GITHUB_TOKEN` _when `CODESPACES` environment variable is set_

The result being `git` sending authentication tokens when cloning submodules.

In `2.63.0`, these GitHub CLI commands will limit the hosts for which `gh` acts as a credential helper to source authentication tokens. Additionally, `GITHUB_TOKEN` will only be used for GitHub.com and ghe.com.

### Impact

Successful exploitation could lead to a third-party using leaked authentication tokens to access privileged resources.

### Remediation and mitigation

1. Upgrade `gh` to `2.63.0`
2. Revoke authentication tokens used with the GitHub CLI: 
    - [Personal access tokens](https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
    - [GitHub CLI OAuth app](https://docs.github.com/en/apps/using-github-apps/reviewing-and-revoking-authorization-of-github-apps#reviewing-your-authorized-github-apps)
3. Review your personal [security log](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log) and any relevant [audit logs](https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/identifying-audit-log-events-performed-by-an-access-token) for actions associated with your account or enterprise

## References
- https://github.com/cli/cli/security/advisories/GHSA-jwcm-9g39-pmcw
- https://nvd.nist.gov/vuln/detail/CVE-2024-53858
- https://git-scm.com/docs/gitcredentials
- https://github.com/cli/cli
