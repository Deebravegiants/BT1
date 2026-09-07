# [H] OpenClaw has a Path Traversal in Plugin Installation

## Summary
Severity: High
Advisory: GHSA-qrq5-wjgg-rvqw
CVE: CVE-2026-28447
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-qrq5-wjgg-rvqw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.20 <2026.2.1

## Details
### Summary

OpenClaw's plugin installation path derivation could be abused by a malicious plugin `package.json` `name` to escape the intended extensions directory and write files to a parent directory.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `>= 2026.1.20, < 2026.2.1`
- Fixed: `>= 2026.2.1`
- Latest published as of 2026-02-14: `2026.2.13` (not affected)

### Details

In affected versions, the plugin installer derives the on-disk install directory from the plugin manifest name without robust validation.

Example (POSIX / macOS / Linux):

- Manifest name: `@malicious/..`
- `unscopedPackageName("@malicious/..")` yields `..`
- The install directory becomes `path.join(extensionsDir, "..")`, which resolves to the parent of the extensions directory.

This can cause plugin files to be written into the OpenClaw state directory (default `~/.openclaw/`) rather than a subdirectory of `~/.openclaw/extensions/`.

Note: on Windows, affected versions also failed to sanitize backslashes (`\\`) in the derived directory name, which can enable deeper traversal via crafted `pluginId` strings.

### Impact

This issue requires a user/operator to install untrusted plugin content (for example via `openclaw plugins install`). In many deployments, plugin installation is an operator-only action and may be performed on a separate machine; that operational separation significantly reduces exposure for the primary gateway/runtime host.

On hosts where untrusted plugins are installed, this can lead to unintended file writes outside the extensions directory (potentially overwriting files under the OpenClaw state directory). On Windows, the traversal surface may extend further, within the privileges of the user running OpenClaw.

### Fix

Fixed in `openclaw` `2026.2.1` by validating plugin IDs and ensuring the resolved install directory remains within the configured extensions base directory.

### Fix Commit(s)

- d03eca8450dc493b198a88b105fd180895238e57

Thanks @logicx24 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qrq5-wjgg-rvqw
- https://nvd.nist.gov/vuln/detail/CVE-2026-28447
- https://github.com/openclaw/openclaw/commit/d03eca8450dc493b198a88b105fd180895238e5
- https://github.com/openclaw/openclaw/commit/d03eca8450dc493b198a88b105fd180895238e57
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.1
- https://www.vulncheck.com/advisories/openclaw-beta-path-traversal-in-plugin-installation-via-package-name
