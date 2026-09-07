# [H] OpenClaw has a path traversal in apply_patch could write/delete files outside the workspace

## Summary
Severity: High
Advisory: GHSA-r5fq-947m-xm57
CVE: CVE-2026-32060
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-r5fq-947m-xm57
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

In affected versions, when `apply_patch` was enabled and the agent ran without filesystem sandbox containment, crafted paths could cause file writes/deletes outside the configured workspace directory.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.13`
- Fixed: `>= 2026.2.14`

## Details

The non-sandbox path resolution in `apply_patch` did not enforce workspace containment. Inputs like `../../...` or absolute paths could escape the working directory in non-sandboxed mode.

## Impact

Practical impact depends on deployment and who can trigger tool execution. This is most relevant when tool invocation is exposed to less-trusted callers or when operators expected workspace-only containment.

## Workarounds

- Keep `tools.exec.applyPatch.enabled` disabled if you do not need `apply_patch`.
- Keep `tools.exec.applyPatch.workspaceOnly` at its secure default of `true`.
- Restrict who can trigger tool execution (and which tools are allowlisted).

## Configuration Note

`tools.exec.applyPatch.workspaceOnly: false` intentionally opts out of workspace containment and can re-enable outside-workspace writes/deletes.

## Fix

- PR: https://github.com/openclaw/openclaw/pull/16405
- Merge commit: `5544646a09c0121fca7d7093812dc2de8437c7f1`

## Credits

Thanks to @p80n-sec for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r5fq-947m-xm57
- https://nvd.nist.gov/vuln/detail/CVE-2026-32060
- https://github.com/openclaw/openclaw/pull/16405
- https://github.com/openclaw/openclaw/commit/5544646a09c0121fca7d7093812dc2de8437c7f1
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
- https://www.vulncheck.com/advisories/openclaw-path-traversal-in-apply-patch-via-crafted-paths
