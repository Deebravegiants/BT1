# [H] pnpm: A tarball dependency's manifest `name` escapes node_modules → arbitrary file write/overwrite on install

## Summary
Severity: High
Advisory: GHSA-vq4v-j7r6-jq4m
CVE: CVE-2026-82393
CWE: CWE-22, CWE-73, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-vq4v-j7r6-jq4m
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.5
- npm: `pnpm` — affected >=11.0.0 <11.11.0

## Details
## Summary
When resolving a package, pnpm uses the resolved **manifest `name`** as a raw path segment for the isolated-linker import target. A tarball dependency whose `package.json` `name` is a scoped path traversal (`@x/../../…/<abs path>`) is therefore extracted **outside `node_modules`**, to an attacker-chosen absolute path, and can **overwrite existing files** there. Attacker controls the destination, filenames, and contents → arbitrary file write → **code execution** (e.g. `~/.zshrc`, `.git/hooks/pre-commit`, another package's code). Occurs during `pnpm install` **even with `--ignore-scripts`** (no lifecycle scripts run), defeating that safety.

Same class as the just-patched **GHSA-hwx4** (transitive-dependency *alias* traversal) and **GHSA-v23m** (`stage download` manifest name/version traversal), in a sink their fixes did not cover: the isolated-linker import target keyed by the resolved **name**.

## Root cause
- The isolated-linker import target is built with a raw `path.join(modules, <resolved name>)` in `installing/deps-resolver/src/resolvePeers.ts:706`, `installing/deps-resolver/src/index.ts:614`, and `deps/graph-builder/src/lockfileToDepGraph.ts:233` — **without** the `safeJoinModulesDir` guard used on the symlink/hoisted/bin paths (`installing/deps-restorer/src/lockfileToHoistedDepGraph.ts:222`). The store location is `node_modules/.pnpm/<id>/node_modules/<name>`, so a traversal `<name>` escapes.
- The only resolve-time name gate (`resolving/npm-resolver/src/pickPackage.ts:753`) rejects only *unscoped* names containing `/`, so a **scoped** `@x/../..` passes.

## Steps to reproduce
Self-contained PoC (real `pnpm@11.9.0`; loopback tarball server; escape target is a throwaway temp dir):
```
npm i pnpm@11.9.0
# host a tarball whose package.json name = "@x/"+"../".repeat(25)+"<abs>/OUTSIDE"; victim depends on the http URL
pnpm install --ignore-scripts
```
Confirmed output (`repro/poc.mjs`, exit 0):
```
escape dir is outside the project        : true
new file implanted outside node_modules  : true
pre-existing file OVERWRITTEN            : true
*** CONFIRMED: a tarball dependency wrote & overwrote files OUTSIDE the project during `pnpm install --ignore-scripts` ***
```

## Remediation
Route the isolated-linker import-target joins (`resolvePeers.ts:706`, `deps-resolver/index.ts:614`, `lockfileToDepGraph.ts:233`) through `safeJoinModulesDir` (as the hoisted linker already does), and/or enforce `validate-npm-package-name` on the resolved manifest name (close the scoped-name gap at `pickPackage.ts:753`) so the import target rejects a traversal name and re-asserts containment before any write.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-vq4v-j7r6-jq4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-82393
- https://github.com/pnpm/pnpm/pull/12872
- https://github.com/pnpm/pnpm/pull/12890
- https://github.com/pnpm/pnpm/commit/51300fd41c5e4c8f47635108e373cc3d1f324fa7
- https://github.com/pnpm/pnpm/commit/78e29fe5583a1e5d69ea05e414eff310f78d5ed9
- https://github.com/pnpm/pnpm
- https://github.com/pnpm/pnpm/releases/tag/v10.34.5
- https://github.com/pnpm/pnpm/releases/tag/v11.11.0
