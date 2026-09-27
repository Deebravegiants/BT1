# [H] Microsoft Kiota Workspace-config poisoning: out-of-repo file write + generation-time SSRF

## Summary
Severity: High
Advisory: GHSA-4rj6-vrwv-wr8m
CVE: CVE-2026-59863
CWE: CWE-22, CWE-829, CWE-918
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-4rj6-vrwv-wr8m
Type: github-advisory

## Affected
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=1.30.0 <1.32.5
- NuGet: `Microsoft.OpenApi.Kiota` — affected >=0 <1.29.1
- NuGet: `Microsoft.OpenApi.Kiota.Builder` — affected >=0 <1.29.1

## Details
### Summary

Microsoft Kiota honors a poisoned `.kiota/workspace.json` — the workspace configuration that Kiota's
documented team workflow has developers commit to their repository — **unvalidated** on
`kiota client generate` / `kiota plugin generate`. A repository (or pull request) containing a malicious
per-client / per-plugin `outputPath` causes Kiota, when a developer or CI runs the documented regenerate
command, to **(CWE-22) write the entire generated client to an arbitrary path outside the workspace** — the
`outputPath` was not confined to the workspace root and absolute paths were accepted.

Confirmed on Kiota **1.32.4** (`KIOTA_CONFIG_PREVIEW=true`, the self-contained `linux-x64` release binary).

### Details

```jsonc
// .kiota/workspace.json (committed to the repo)
"clients": { "MyClient": {
   "outputPath": "/abs/path/outside/repo/pwned_client"   // -> generated client written here (CWE-22)
}}
```

Running `kiota client generate --client-name MyClient` in the repo writes `MyClient.cs`,
`P/PRequestBuilder.cs`, … to the attacker-chosen `outputPath` (verified outside the working tree).

#### Note on `descriptionLocation`

The per-consumer `descriptionLocation` is intentionally fetched at generation time — this is how Kiota knows
where to pull an updated description from when refreshing a client, the same way any other value in a
committed lock/config file is honored. It is **not** treated as a vulnerability and is unchanged; only
`outputPath` is now confined.

### Impact

A malicious or compromised repository — or a malicious PR that edits `.kiota/workspace.json` — leads to
arbitrary file write on the developer's or CI host's filesystem (overwrite source/build files, drop files in
auto-loaded locations) whenever a teammate clones/pulls and runs the documented `kiota client generate` /
`kiota plugin generate` to refresh the client. CWE-22.

This is a different trust boundary from the OpenAPI-description-based findings: the malicious input is the
Kiota **config**, not the spec.

### Patches

Fixed in **1.29.1 and 1.32.5** (https://github.com/microsoft/kiota/pull/7885). On loading a workspace configuration,
each client/plugin `outputPath` is validated to be a relative subdirectory of the workspace: null/empty,
rooted paths (POSIX `/`, UNC `\\` / `//`, Windows drive `X:\`), and any `..` traversal segment are rejected,
and the resolved full path must stay under the workspace root. Generation aborts with an error if any
consumer's `outputPath` escapes the workspace.

### Remediation

Upgrade to Kiota **1.29.1, 1.32.5** or later. Review any committed workspace configs for `outputPath` values that
point outside the workspace.

## References
- https://github.com/microsoft/kiota/security/advisories/GHSA-4rj6-vrwv-wr8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-59863
- https://github.com/microsoft/kiota/pull/7885
- https://github.com/microsoft/kiota/commit/4049327872db7846ace35c9003774d3e3878e4e9
- https://github.com/microsoft/kiota
- https://github.com/microsoft/kiota/releases/tag/v1.32.5
