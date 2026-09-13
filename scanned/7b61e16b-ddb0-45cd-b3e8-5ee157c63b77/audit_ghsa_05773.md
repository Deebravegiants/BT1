# [M] Tekton Pipelines-as-Code: Unscoped GitHub App installation token allows unauthorized access to private repositories via remote task resolution

## Summary
Severity: Medium
Advisory: GHSA-6f2p-296r-cc28
CVE: CVE-2026-54168
CWE: CWE-269, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-6f2p-296r-cc28
Type: github-advisory

## Affected
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0 <0.37.8
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0.38.0 <0.39.6
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0.40.0 <0.42.1
- Go: `github.com/openshift-pipelines/pipelines-as-code` — affected >=0.43.0 <0.48.0

## Details
### Impact
When Pipelines-as-Code is configured with a GitHub App installed across multiple repositories, the installation token issued during webhook processing is not scoped to the triggering repository by default. The token retains access to all repositories in the GitHub App installation.

This allows a user with push access to any repository in the installation to craft a PipelineRun with a remote task annotation pointing at a private repository in the same installation:
```
pipelinesascode.tekton.dev/task: "https://github.com/org/private-repo/blob/main/.tekton/secret-task.yaml"
```
Pipelines-as-Code resolves and inlines the remote task using the unscoped token, exposing the contents of the private repository's Tekton definitions. This is a read-only confidentiality breach, no write access is exposed.

### Patches
The fix extracts the repository ID from the webhook payload during initial parsing so that it is available for later use. It then adds a fallback in the client setup path so that when no explicit scoping configuration is present and `ScopeTokenToListOfRepos` returns empty, the token is re-issued scoped to the triggering repository's ID rather than retaining access to the entire installation. The initial token remains unscoped so that the extra-repos lookup can still discover and resolve additional repositories when configured.

The fix is available in v0.48.0. Supported backport releases will be added here after release tags are published.

### Workarounds
Limit the GitHub App installation to only the repositories that require Pipelines-as-Code. Avoid org-wide installations or mixed-trust installations where repositories with different access requirements share the same GitHub App. This restricts the blast radius of the unscoped token to only the repositories that are explicitly selected during App installation.

### Credits
Reported and fixed by the Pipelines-as-Code maintainers.

## References
- https://github.com/tektoncd/pipelines-as-code/security/advisories/GHSA-6f2p-296r-cc28
- https://github.com/tektoncd/pipelines-as-code
