# [M] OpenClaw ACP client has permission auto-approval bypass via untrusted tool metadata

## Summary
Severity: Medium
Advisory: GHSA-7jx5-9fjg-hp4m
CVE: CVE-2026-32898
CWE: CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-7jx5-9fjg-hp4m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
## Vulnerability Summary

The OpenClaw ACP client could auto-approve tool calls based on untrusted metadata and permissive name heuristics. A malicious or compromised ACP tool invocation could bypass expected interactive approval prompts for read-class operations.

## Affected Packages / Versions

- Package: npm `openclaw`
- Affected published versions: `<= 2026.2.22-2` (latest published as of February 24, 2026 is `2026.2.22-2`)
- Patched in code on `main`: `2026.2.23` (released)

## Technical Details

- Permission classification trusted incoming `toolCall.kind` and heuristic name matching.
- Non-core read-like names and spoofed kind metadata could reach auto-approve paths.
- `read` operations were not scoped strongly enough to cwd in all metadata/title forms.

## Fix

- Require trusted core tool IDs for auto-approval and ignore untrusted `toolCall.kind` as an authorization source.
- Scope `read` auto-approval to cwd-resolved paths.
- Add stricter tool-name validation and regression coverage for spoofed kind and non-core read-like names.

## Affected Functions

- `resolvePermissionRequest`
- `resolveToolNameForPermission`
- `shouldAutoApproveToolCall`

## Fix Commit(s)

- `12cc754332f9a7c92e158ce7644aa22df79c0904`
- `63dcd28ae0be2de1c75af09cc81841cebeec068f`

Found using [MCPwner](https://github.com/Pigyon/MCPwner)


Thanks @nedlir for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7jx5-9fjg-hp4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32898
- https://github.com/openclaw/openclaw/commit/12cc754332f9a7c92e158ce7644aa22df79c0904
- https://github.com/openclaw/openclaw/commit/63dcd28ae0be2de1c75af09cc81841cebeec068f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.23
- https://www.vulncheck.com/advisories/openclaw-acp-permission-auto-approval-bypass-via-untrusted-tool-metadata
