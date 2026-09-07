# [M] `auth.TokenForHost` violates GitHub host security boundary when sourcing authentication token within a codespace

## Summary
Severity: Medium
Advisory: GHSA-55v3-xh23-96gh
CVE: CVE-2024-53859
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-11-27
Source: https://github.com/advisories/GHSA-55v3-xh23-96gh
Type: github-advisory

## Affected
- Go: `github.com/cli/go-gh/v2` — affected >=0 <2.11.1
- Go: `github.com/cli/go-gh` — affected >=0

## Details
### Summary

A security vulnerability has been identified in `go-gh` that could leak authentication tokens intended for GitHub hosts to non-GitHub hosts when within a codespace.

### Details

`go-gh` sources authentication tokens from different environment variables depending on the host involved:

- `GITHUB_TOKEN`, `GH_TOKEN` for GitHub.com and ghe.com
- `GITHUB_ENTERPRISE_TOKEN`, `GH_ENTERPRISE_TOKEN` for GitHub Enterprise Server

Prior to `2.11.1`, `auth.TokenForHost` could source a token from the `GITHUB_TOKEN` environment variable for a host other than GitHub.com or ghe.com when [within a codespace](https://github.com/cli/go-gh/blob/71770357e0cb12867d3e3e288854c0aa09d440b7/pkg/auth/auth.go#L73-L77).

In `2.11.1`, `auth.TokenForHost` will only source a token from the `GITHUB_TOKEN` environment variable for GitHub.com or ghe.com hosts.

### Impact

Successful exploitation could send authentication token to an unintended host. 

### Remediation and mitigation

1. Upgrade `go-gh` to `2.11.1`
2. Advise extension users to regenerate authentication tokens:
    - [Personal access tokens](https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
    - [GitHub CLI OAuth app](https://docs.github.com/en/apps/using-github-apps/reviewing-and-revoking-authorization-of-github-apps#reviewing-your-authorized-github-apps)
3. Advise extension users to review their personal [security log](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log) and any relevant [audit logs](https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/identifying-audit-log-events-performed-by-an-access-token) for actions associated with their account or enterprise

## References
- https://github.com/cli/go-gh/security/advisories/GHSA-55v3-xh23-96gh
- https://nvd.nist.gov/vuln/detail/CVE-2024-53859
- https://docs.github.com/en/apps/using-github-apps/reviewing-and-revoking-authorization-of-github-apps#reviewing-your-authorized-github-apps
- https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log
- https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/identifying-audit-log-events-performed-by-an-access-token
- https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- https://github.com/cli/go-gh
- https://github.com/cli/go-gh/blob/71770357e0cb12867d3e3e288854c0aa09d440b7/pkg/auth/auth.go#L73-L77
- https://pkg.go.dev/vuln/GO-2024-3295
