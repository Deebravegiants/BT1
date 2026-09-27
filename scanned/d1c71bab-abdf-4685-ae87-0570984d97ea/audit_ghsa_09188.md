# [C] Coder: PKCS#7 signature bypass in Azure instance identity allows unauthenticated agent token theft

## Summary
Severity: Critical
Advisory: GHSA-6x44-w3xg-hqqf
CVE: CVE-2026-46354
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-6x44-w3xg-hqqf
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.33.0-rc.0 <2.33.3
- Go: `github.com/coder/coder/v2` — affected >=2.32.0-rc.0 <2.32.2
- Go: `github.com/coder/coder/v2` — affected >=2.31.0 <2.31.12
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.30.8
- Go: `github.com/coder/coder/v2` — affected >=2.29.0 <2.29.13
- Go: `github.com/coder/coder/v2` — affected >=0 <2.24.5
- Go: `github.com/coder/coder` — affected >=0

## Details
## Summary

`azureidentity.Validate()` verifies that the PKCS#7 signer certificate chains to a trusted Azure CA but never verifies the PKCS#7 signature itself. An attacker can embed a legitimate Azure certificate alongside arbitrary content e.g. `{"vmId":"<target>"}` and the forged `vmId` will be accepted returning the victim workspace agent's session token.

**No authentication is required.** The attacker only needs to know a target VM's `vmId` which is a `UUIDv4`.
> that's a practical limitation which would typically require prior access to be exploited

## Root Cause

In unpatched Coder releases the signature over the PKCS#7 content is not validated - only the signing certificate is checked.

## Impact

An attacker on any Azure VM or with access to a publicly available Azure IMDS certificate from CT logs can:

1. **Steal an agent session token** by sending a forged PKCS#7 envelope to `POST /api/v2/workspaceagents/azure-instance-identity` which is unauthenticated.
2. **With the stolen token** access:
   - **Git SSH private key** via `GET /workspaceagents/me/gitsshkey`: push to repositories and impersonate the workspace owner.
   - **OAuth access tokens** via `GET /workspaceagents/me/external-auth`: GitHub, GitLab, and Bitbucket tokens in plaintext.
   - **Workspace secrets** via the agent manifest: environment variables, file paths, and API keys.

## Attack Path Diagram

<img width="5588" height="4176" alt="PKCS7_diagram (1)" src="https://github.com/user-attachments/assets/74e88a89-a995-450d-87ab-6feed03579a5" />

## Affected Versions

All versions of Coder v2 are affected.

## Patches

Fixed in [#25286 ](https://github.com/coder/coder/pull/25286)

The fix was backported to all supported release lines:

| Patched Versions |
| --- |
| [**v2.33.3**](https://github.com/coder/coder/releases/tag/v2.33.3) |
| [**v2.32.2**](https://github.com/coder/coder/releases/tag/v2.32.2) |
| [**v2.31.12**](https://github.com/coder/coder/releases/tag/v2.31.12) |
| [**v2.30.8**](https://github.com/coder/coder/releases/tag/v2.30.8) |
| [**v2.29.13**](https://github.com/coder/coder/releases/tag/v2.29.13) |
| [**v2.24.5**](https://github.com/coder/coder/releases/tag/v2.24.5) |

## Workarounds

If unable to patch we recommend immediately reconfiguring any Azure templates to use token authentication rather than `azure-instance-identity` until the patch is released and you are fully upgraded.

1. Modify the [`coder_agent.auth`](https://registry.terraform.io/providers/coder/coder/latest/docs/resources/agent#auth-1) value to be `token`.
2. Add `CODER_AGENT_TOKEN=${coder_agent.main.token}` to the set of environment variables for the Coder Workspace Agent initialization script.

## Recognition

We'd like to thank [Ben Tran](https://github.com/bencalif) of [calif.io](http://calif.io) and Anthropic’s Security Team (`ANT-2026-22445`) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-6x44-w3xg-hqqf
- https://github.com/coder/coder/pull/25286
- https://github.com/coder/coder
- https://github.com/coder/coder/releases/tag/v2.24.5
- https://github.com/coder/coder/releases/tag/v2.29.13
- https://github.com/coder/coder/releases/tag/v2.30.8
- https://github.com/coder/coder/releases/tag/v2.31.12
- https://github.com/coder/coder/releases/tag/v2.32.2
- https://github.com/coder/coder/releases/tag/v2.33.3
