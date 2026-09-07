# [H] Pipelines-as-Code GitHub App token request can be redirected via untrusted Enterprise Host header

## Summary
Severity: High
Advisory: GHSA-f5f4-3hh4-f54m
CVE: CVE-2026-54167
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-f5f4-3hh4-f54m
Type: github-advisory

## Affected
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0.43.0 <0.48.0
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0.40.0 <0.42.1
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0.38.0 <0.39.6
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0 <0.37.8

## Details
## Impact

Pipelines-as-Code installations using the GitHub App provider are vulnerable to GitHub App credential exfiltration through the webhook endpoint.

Affected versions accepted the `X-GitHub-Enterprise-Host` request header as the GitHub Enterprise API host during GitHub App token generation. For GitHub webhook events containing an `installation.id`, Pipelines-as-Code generated a GitHub App JWT and requested an installation access token before validating the webhook signature or checking that the Enterprise host matched the repository URL in the signed payload.

An attacker who can reach the Pipelines-as-Code webhook endpoint can send a crafted GitHub webhook payload containing an installation ID and set `X-GitHub-Enterprise-Host` to an attacker-controlled host. During token generation, the controller signs a GitHub App JWT locally and sends it to the selected API host. This can disclose the GitHub App JWT to the attacker-controlled service, allowing the attacker to attempt to mint GitHub App installation access tokens within the JWT validity window, subject to the GitHub App installation and permissions.

The incoming webhook flow also trusted `X-GitHub-Enterprise-Host` during GitHub App installation lookup and token generation. In that path, exploitation requires a valid incoming webhook secret for the target Repository CR.

## Patches

The fix validates the webhook signature before GitHub App token generation, verifies that `X-GitHub-Enterprise-Host` matches the repository URL in the webhook payload, and stops using the request header to select the GitHub Enterprise host for incoming webhook token requests. For incoming webhooks, the Enterprise host is derived from the configured Repository URL instead.

The fix is available in v0.48.0. Supported backport releases will be added here after release tags are published.

## Workarounds

Until a patched release is deployed, operators should block or strip unexpected `X-GitHub-Enterprise-Host` headers at the ingress or proxy in front of the Pipelines-as-Code webhook endpoint. For GitHub.com installations, reject requests that include this header. For GitHub Enterprise Server installations, allow only the expected Enterprise hostname.

Operators should also restrict access to the webhook endpoint to trusted Git provider sources where possible. If exploitation is suspected, rotate the GitHub App private key and review GitHub App installation token activity.

## Credits

Reported and fixed by the Pipelines-as-Code maintainers.

## References
- https://github.com/tektoncd/pipelines-as-code/security/advisories/GHSA-f5f4-3hh4-f54m
- https://github.com/tektoncd/pipelines-as-code
