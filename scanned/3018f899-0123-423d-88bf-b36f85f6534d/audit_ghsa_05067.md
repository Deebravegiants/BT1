# [H] pnpm: Hoisted install imports lockfile alias outside node_modules

## Summary
Severity: High
Advisory: GHSA-fr4h-3cph-29xv
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-27
Source: https://github.com/advisories/GHSA-fr4h-3cph-29xv
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.4
- npm: `pnpm` — affected >=11.0.0 <11.7.0

## Details
## Summary

The hoisted dependency alias issue tracked as GHSA-fr4h-3cph-29xv / CAND-PNPM-059 has been addressed in both pnpm and pacquet.

A crafted lockfile alias could be joined directly under a hoisted `node_modules` directory. Traversal aliases could escape that directory, while reserved aliases such as `.bin` or `.pnpm` could overwrite pnpm-owned layout. This patch validates package-name semantics and path containment before graph insertion or filesystem work.

## Security boundary

- The TypeScript hoisted graph uses the shared safe join helper at the actual `dep.name` sink.
- The helper rejects traversal, absolute, platform-specific, and reserved package names.
- Pacquet validates the hoister's `dep.0.name` before adding the graph node or recursing.
- Both implementations return `ERR_PNPM_INVALID_DEPENDENCY_NAME`.
- Pacquet uses the same dependency-name containment rule at its hoisted graph sink as it uses for direct dependency aliases.

## Exploit replay

Before the patch, a traversal alias in a hoisted lockfile imported package files outside the intended install root. With this patch, both pnpm and pacquet reject the alias before graph insertion or filesystem work, and the escaped file is not created.

## Files changed

- `fs/symlink-dependency/src/safeJoinModulesDir.ts` provides the TypeScript containment helper.
- `installing/deps-restorer/src/lockfileToHoistedDepGraph.ts` validates the parsed dependency name at the hoisted graph sink.
- `pacquet/crates/package-manager/src/{hoisted_dep_graph.rs,safe_join_modules_dir.rs}` mirrors that boundary in Rust.
- TypeScript and Rust tests cover traversal, reserved aliases, and valid scoped names.

## Commands run

```text
$ pnpm --filter @pnpm/fs.symlink-dependency test
PASS: 24 tests
$ pnpm --filter @pnpm/installing.deps-restorer test test/index.ts
PASS: exploit regression and positive install control
$ cargo test --locked -p pacquet-package-manager --lib
PASS: 426 tests
$ cargo fmt --all -- --check
PASS
```

## Validation

- TypeScript symlink helper: 24 passed.
- TypeScript exploit regression: 1 passed.
- TypeScript positive hoisted-install control: 1 passed.
- Targeted strict TypeScript compiles: passed.
- Targeted ESLint: zero errors.
- Pacquet helper tests: 3 passed.
- Full pacquet package-manager library suite: 426 passed.
- `cargo fmt`, parsed two-document lockfile validation, and `git diff --check`: passed.

## Patch

Ready-for-review private PR: https://github.com/pnpm/pnpm-ghsa-fr4h-3cph-29xv/pull/1

GitHub reports the branch as mergeable and has requested review from `zkochan`. GitHub intentionally does not run status checks on temporary private-fork PRs; the commands and outcomes above are the recorded local validation: https://docs.github.com/code-security/security-advisories/collaborating-in-a-temporary-private-fork-to-resolve-a-security-vulnerability

## Compatibility

Valid unscoped and scoped package aliases continue to work. The changeset covers `@pnpm/fs.symlink-dependency`, `@pnpm/installing.deps-restorer`, and `pnpm`; pacquet is updated in the same commit for CLI parity.

---
Written by an agent (Codex, GPT-5).

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-fr4h-3cph-29xv
- https://github.com/pnpm/pnpm
