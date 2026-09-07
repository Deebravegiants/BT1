# [H] GitHub CLI has an incorrect authorization header in API requests to TUF repository mirrors via `gh attestation`, `gh release verify`, and `gh release verify-asset` commands

## Summary
Severity: High
Advisory: GHSA-8xvp-7hj6-mcj9
CVE: CVE-2026-48501
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-8xvp-7hj6-mcj9
Type: github-advisory

## Affected
- Go: `github.com/cli/cli/v2` — affected >=0 <2.93.0

## Details
### Summary

GitHub CLI incorrectly includes an authorization header in API requests to TUF repository mirrors via `gh attestation`, `gh release verify`, and `gh release verify-asset` commands.

 **Affected users:**

  - Authenticated `github.com` users who previously ran `gh attestation` commands, `gh release verify`, or `gh release verify-asset`: the `github.com` token was included in requests to `tuf-repo.github.com`, a GitHub Pages domain that is not a GitHub API endpoint. All authentication types are affected.
  - Users with `GH_ENTERPRISE_TOKEN` or `GITHUB_ENTERPRISE_TOKEN` set who previously ran `gh attestation` commands, `gh release verify`, or `gh release verify-asset`: the enterprise token was included in requests to external hosts `tuf-repo-cdn.sigstore.dev` and `tmaproduction.blob.core.windows.net`. These hosts are not operated by GitHub.

### Details

The CLI uses a shared HTTP client with an authentication layer that automatically attaches tokens to outgoing requests. This layer lacks accurate host detection and can incorrectly attribute the target host, providing it with a token it should never receive.

Specifically, the host normalization logic collapses any `*.github.com` subdomain to `github.com`, so a request to `tuf-repo.github.com` (a GitHub Pages site, not a GitHub API endpoint) is treated as a request to `github.com` and receives the user's github.com token. For hosts that don't match `github.com` or a known GHES instance at all, the resolver falls back to `GH_ENTERPRISE_TOKEN` if set.

The `gh attestation`, `gh release verify` and `gh release verify-asset` commands fetch data from several external hosts as part of their normal operation (TUF metadata from `tuf-repo.github.com` and `tuf-repo-cdn.sigstore.dev`, artifact bundles from Azure Blob Storage). Because these requests go through the same authenticated HTTP client, the token is sent to all of them.

### Impact

Tokens were transmitted in HTTP headers to the listed hosts during normal `gh attestation`, `gh release verify`, and `gh release verify-asset` operations. There is no evidence that tokens were logged, retained, or accessed by unauthorized parties. If a token were captured, it would grant the same access as the token holder, potentially including private repositories, organization resources, or enterprise administration depending on token type and permissions.

### Remediation and mitigation

1. Revoke authentication tokens used with the GitHub CLI: 
    - [Personal access tokens](https://docs.github.com/en/enterprise-cloud@latest/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
    - [GitHub CLI OAuth app](https://docs.github.com/en/apps/using-github-apps/reviewing-and-revoking-authorization-of-github-apps#reviewing-your-authorized-github-apps)
2. Upgrade `gh` to `2.93.0`.
3. Review personal [security logs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log) and any relevant [audit logs](https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/identifying-audit-log-events-performed-by-an-access-token) for actions associated with personal or enterprise accounts.

## References
- https://github.com/cli/cli/security/advisories/GHSA-8xvp-7hj6-mcj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48501
- https://github.com/cli/cli
- https://github.com/cli/cli/releases/tag/v2.93.0
