# [H] pnpm: Manifest identity spoof satisfies allowBuilds and runs attacker lifecycle

## Summary
Severity: High
Advisory: GHSA-5wx6-mg75-v57r
CVE: CVE-2026-55487
CWE: CWE-346, CWE-693, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-5wx6-mg75-v57r
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.2
- npm: `pnpm` — affected >=11.0.0 <11.5.3

## Details
## Summary

Keep build approval for opaque dependency sources byte-exact for GHSA-5wx6-mg75-v57r / CAND-PNPM-123.

Merged upstream commit `bf1b731ee6` fixed the original name-only approval bypass by making build policy consume the resolved dependency identity. One collision remained: the generic peer-suffix normalizer also stripped parenthesized text from git, URL, tarball, file, and other opaque locators. Approval for one source string could therefore authorize a different attacker-controlled source whose locator normalized to the same value.

## Security boundary

- Registry dependency identities still normalize legitimate peer suffixes and retain patch hashes.
- Git, URL, tarball, file, directory, and otherwise opaque identities must match the complete resolved locator byte for byte.
- Explicit denials use the same normalization as approvals.
- Ignored-build output preserves the exact opaque identity, so the key pnpm asks a user to approve is the key policy later checks.
- TypeScript pnpm and pacquet implement the same distinction between registry and opaque identities.

## Exploit replay

- With `allowBuilds` approving `foo@https://host/pkg.tgz`, the upstream implementation also accepted `foo@https://host/pkg.tgz(evil)` because both passed through peer-suffix removal.
- An independent review found a second Rust-only form: `foo@https://host/pkg@1.0.0(good)` and `foo@https://host/pkg@1.0.0(evil)` collided because the parser selected the final `@` and misclassified the opaque URL as a registry package.
- A final review found the same parser hazard in source-only locators ending in a semver-looking tail: approval for `https://host/pkg@1.0.0` could collapse `https://host/pkg@1.0.0(evil)`.
- The final patch rejects all three collision forms, applies the same exactness to deny rules, accepts exact opaque keys as positive controls, and continues to accept registry packages approved without their peer suffixes.

## Files changed

- `building/policy/src/index.ts` and `building/policy/test/index.ts` normalize only parsed registry identities and retain exact opaque keys.
- `pacquet/crates/package-manager/src/build_modules.rs` passes snapshot identities to policy, matches TypeScript package-separator parsing, and preserves opaque locators.
- `pacquet/crates/package-manager/src/build_modules/tests.rs` covers exact approval and denial, all three collision forms, ignored-build output, and registry peer compatibility.
- `.changeset/quiet-opaque-build-identities.md` records patch releases for `@pnpm/building.policy` and `pnpm`.

## Commands run

```text
$ jest building/policy/test/index.ts --runInBand
16 passed
$ cargo test -p pacquet-package-manager build_modules::tests -- --nocapture
49 passed
$ cargo fmt --all -- --check
PASS
$ git diff --check 84bb4b1a046f3a659de1c9aab1d45dcf814124ce...HEAD
PASS
```

## Validation

- The TypeScript policy suite passed all 16 tests.
- The final pacquet build-policy suite passed all 49 tests.
- The new Rust regression reproduced the extra-`@` collision before the additive fix and passed afterward.
- Exact opaque approval and denial, source-only semver-tail collision rejection, registry peer normalization, and ignored-build reporting all have paired tests.
- ESLint passed on the changed TypeScript source and test files.
- Rust formatting and diff checks passed; the branch is clean and consists of three focused security commits plus additive merges of upstream through `84bb4b1a046f3a659de1c9aab1d45dcf814124ce`.
- The focused TypeScript suite and ESLint ran directly through the installed harness. The isolated project build cannot resolve workspace packages without a local install, and the configured registry gateway returns HTTP 403 while fetching `@pnpm/pacquet@0.11.2`; no candidate-focused test failed.

## Patches

`10.34.2`: https://github.com/pnpm/pnpm/commit/14bceb1e0b2a71f4f670774db261feb03f38ec23
`11.5.3`: https://github.com/pnpm/pnpm/commit/bf1b731ee6c0ea98709e671ff0f46bf654480ab8

## Compatibility

Registry package approvals keep their existing form. Opaque dependencies that were approved through a normalized parenthesized variant must now use the exact key shown in pnpm's ignored-build output. This is the intended trust-boundary change; no package-resolution or artifact format changes.

## CI note

GitHub intentionally does not run status checks on temporary private-fork pull requests. The complete policy suites, formatting, and diff checks above are the applicable validation: https://docs.github.com/code-security/security-advisories/collaborating-in-a-temporary-private-fork-to-resolve-a-security-vulnerability

---
Written by an agent (Codex, GPT-5).

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-5wx6-mg75-v57r
- https://nvd.nist.gov/vuln/detail/CVE-2026-55487
- https://github.com/pnpm/pnpm/commit/bf1b731ee6c0ea98709e671ff0f46bf654480ab8
- https://github.com/pnpm/pnpm
- https://github.com/pnpm/pnpm/releases/tag/v10.34.2
- https://github.com/pnpm/pnpm/releases/tag/v11.5.3
