# [C] @vitest/browser: Browser Mode provider commands bypass the file-access permission gate

## Summary
Severity: Critical
Advisory: GHSA-p63j-vcc4-9vmv
CVE: CVE-2026-73653
CWE: CWE-22, CWE-552, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-p63j-vcc4-9vmv
Type: github-advisory

## Affected
- npm: `@vitest/browser` — affected >=4.0.0 <4.1.10
- npm: `@vitest/browser` — affected >=0 <3.2.7
- npm: `@vitest/browser` — affected >=5.0.0-beta.1 <5.0.0-beta.6

## Details
## Summary

Browser Mode exposes a set of built-in "commands" that run on the Node.js side of the test runner and can touch the local filesystem (taking screenshots, managing Playwright traces, uploading files for `<input type="file">`, comparing screenshots).

Several of these commands accept a file path from the browser and act on it without checking the `allowWrite` permission gate and without confining the path to the project directory. A client that can reach the Browser Mode API can therefore read, create, overwrite, or delete files anywhere the Vitest process can access, even when `allowWrite` is `false`.

This matters most when the Browser Mode API is exposed to the network (for example `test.api.host` is set, or the dev server is reachable from another machine or origin). In that configuration `allowWrite` defaults to `false` precisely to block file access, and these commands bypass that protection. On a default localhost-only setup with trusted test code, there is no untrusted party in a position to exploit it. The gap still matters wherever you rely on `allowWrite: false` to contain untrusted test code, because these commands ignore that flag.

## Affected commands and impact

| Command | Operation | Impact |
|---|---|---|
| `upload` (Playwright + WebdriverIO) | Read | Arbitrary local file read; contents are loaded into the page and readable by test code. Highest-impact case. |
| `takeScreenshot` (Playwright + WebdriverIO) | Write | Writes a PNG to an arbitrary path (absolute path used verbatim), creating parent directories. |
| `screenshotMatcher` | Write | Writes reference/diff PNGs; directory derived from client path allows partial traversal. |
| `stopChunkTrace` | Write | Writes a Playwright trace `.zip` to a path escapable via `../` in the trace name. |
| `deleteTracing` | Delete | Deletes arbitrary files by path. |
| `annotateTraces` | Read (disclosure) | Records a client-controlled attachment path that the reporter copies into the attachments directory, disclosing file contents. |

The writes do not let an attacker choose the file contents (they produce PNG images or trace archives), so the integrity impact is creating, overwriting, or deleting a file at an arbitrary path rather than writing a chosen payload. The reads (`upload`, `annotateTraces`) are more serious because they expose the full contents of an arbitrary file.

The fix adds, to every file-touching provider command, an `allowWrite` check for write/delete operations and path confinement to the project root (matching the existing `fs` command pattern), so client-supplied absolute paths and `../` traversal are rejected.

## References
- https://github.com/vitest-dev/vitest/security/advisories/GHSA-p63j-vcc4-9vmv
- https://github.com/vitest-dev/vitest/pull/10674
- https://github.com/vitest-dev/vitest/pull/10679
- https://github.com/vitest-dev/vitest/pull/10680
- https://github.com/vitest-dev/vitest/commit/33f96a145ef09ca6a43b4e555eb273e64a87be23
- https://github.com/vitest-dev/vitest/commit/5c18dd267ff7f47f24cab2f615a16b37d90feb7f
- https://github.com/vitest-dev/vitest/commit/b795e36b34969bec50b47a9f29d26f799a6a04fb
- https://github.com/vitest-dev/vitest
- https://github.com/vitest-dev/vitest/releases/tag/v3.2.7
- https://github.com/vitest-dev/vitest/releases/tag/v4.1.10
- https://github.com/vitest-dev/vitest/releases/tag/v5.0.0-beta.6
