# [H] pnpm: `patch-remove` could delete project-selected files outside the patches directory

## Summary
Severity: High
Advisory: GHSA-72r4-9c5j-mj57
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-27
Source: https://github.com/advisories/GHSA-72r4-9c5j-mj57
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.4
- npm: `pnpm` — affected >=11.0.0 <11.7.0

## Details
## Summary

The `patch-remove` deletion-scope issue tracked as GHSA-72r4-9c5j-mj57 / CAND-PNPM-030 has been addressed in pnpm.

A crafted patch entry could resolve outside the configured patches directory and cause `pnpm patch-remove` to delete an arbitrary reachable file. This patch validates the configured directory and every resolved target before unlinking anything, then deletes the final directory entry without following it.

## Security boundary

- Traversal and absolute paths that resolve outside the configured patches directory are rejected before deletion.
- Parent directories are canonicalized before deletion, including the case where a nested symlink points outside and the final outside entry is itself dangling.
- The complete batch is validated before any file is removed.
- Component-aware predicates accept valid names beginning with `..` while still rejecting parent traversal, Windows drive escapes, and UNC escapes.
- Valid files and symlinked patch directories whose canonical targets remain below the lockfile directory continue to work.
- A final symlink inside a valid patch directory is unlinked without following its target, including when the target is outside or dangling.

## Exploit replay

Before the patch, a workspace `patchedDependencies` path that resolved outside the project caused `pnpm patch-remove` to delete the external sentinel. A second replay used a nested parent symlink and a dangling outside victim: `realpath()` returned `ENOENT`, yet the victim was still removed. With this patch, both paths are rejected and the outside entries remain intact.

## Files changed

- `patching/commands/src/isSubdirectory.ts` performs component-aware containment checks.
- `patching/commands/src/patchRemove.ts` validates the full batch, canonicalizes parents, and unlinks final entries without following them.
- `patching/commands/test/{isSubdirectory,patchRemove}.test.ts` covers traversal, nested symlinks, dangling victims, and valid removals.

## Commands run

```text
$ pnpm --filter @pnpm/patching.commands test test/isSubdirectory.test.ts test/patchRemove.test.ts
PASS: 11 tests across 2 suites
$ pnpm --filter @pnpm/patching.commands run compile
PASS
$ git diff --check
PASS
```

## Validation

- Focused handler and path-predicate suites: 11 passed across 2 suites.
- Package-wide ESLint: passed.
- Package TypeScript build: passed.
- Commit hooks, Commitlint, and `git diff --check`: passed.
- The broader integration harness was environment-blocked because it writes outside the available temporary root; focused handler tests used `/private/tmp`.

## Patches

`10.34.4`: https://github.com/pnpm/pnpm/commit/352ae489f1b14ffdc19d2c6eacb1b06b098c2ddc
`11.7.0`: https://github.com/pnpm/pnpm/commit/612a2e6a7333f2b061f452a21b6e62c1c161747f

## Compatibility

Missing patch files remain no-ops. Valid symlinked patch directories continue to work when their canonical target stays inside the lockfile directory, and final symlinks are removed without touching their targets. `patch-remove` is not yet in pacquet's command surface, so no Rust-side parity change is required.

## Remaining risk

Portable Node APIs do not expose directory-fd-relative `unlinkat()`. A local attacker who can replace an already validated parent directory before the unlink may still win a time-of-check/time-of-use race. The reproduced repository-controlled traversal and symlink paths do not require that concurrent capability and are blocked by this patch.

---
Written by an agent (Codex, GPT-5).

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-72r4-9c5j-mj57
- https://github.com/pnpm/pnpm/commit/612a2e6a7333f2b061f452a21b6e62c1c161747f
- https://github.com/pnpm/pnpm
- http://github.com/pnpm/pnpm/commit/352ae489f1b14ffdc19d2c6eacb1b06b098c2ddc
