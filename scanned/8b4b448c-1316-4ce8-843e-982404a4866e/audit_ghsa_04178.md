# [H] pnpm: Repository-controlled configDependencies can select a pacquet native install engine

## Summary
Severity: High
Advisory: GHSA-gj8w-mvpf-x27x
CVE: CVE-2026-55697
CWE: CWE-494, CWE-78, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-gj8w-mvpf-x27x
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.2
- npm: `pnpm` — affected >=11.0.0 <11.5.3

## Details
<!-- maintainer-action:start -->
## Maintainer Action Plan

This report is ready to review with the shared patch branch. Start with the PR and the expected fixed behavior, then use the detailed exploit narrative below only if you want to replay the original path.

- Advisory: `CAND-PNPM-097` / `GHSA-gj8w-mvpf-x27x`
- Advisory URL: https://github.com/pnpm/pnpm/security/advisories/GHSA-gj8w-mvpf-x27x
- Shared patch PR: https://github.com/pnpm/pnpm-ghsa-j2hc-m6cf-6jm8/pull/1
- Shared patch branch: `security/ghsa-batch-2026-06-09`
- Patch commit: `a93449314f398cf4bdf2e28d033c02d37395ad22`
- Base commit: `origin/main` `55a4035abf1ae3fe7208ba1f5ef43c5eff58ccec`
- Maintainer priority: `start-here`
- Component: `pnpm configDependencies / pacquet delegation`
- Patch area: pacquet/configDependency lifecycle execution is not used as install engine without trust
- Affected packages: `npm:pnpm`, `npm:@pnpm/config.reader`, `npm:@pnpm/installing.commands`
- CWE IDs: `CWE-829`, `CWE-78`, `CWE-494`
- Conservative CVSS: `7.5` / `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H`
- Next action: review the shared patch branch for this component, set the final affected version range, merge and release the fix, then publish or close the advisory.

### Expected Patched Behavior

config-dependency pacquet install engines are not selected unless the trusted allowlist is set outside the repository; the marker file is not created.

### Files And Tests To Review

- `config/reader/src/Config.ts`
- `config/reader/src/types.ts`
- `config/reader/src/configFileKey.ts`
- `config/reader/src/index.ts`
- `config/reader/test/index.ts`
- `installing/commands/src/installDeps.ts`
- `installing/commands/test/runPacquet.ts`
- `pnpm/test/install/pacquet.ts`
- `.changeset/lucky-config-plugin-pnpmfiles.md`

### Focused Validation

Run these from a checkout of the shared patch branch. They are the useful maintainer commands with machine-local artifact paths removed.

```bash
./node_modules/.bin/tsgo --build config/reader/tsconfig.json
./node_modules/.bin/tsgo --build installing/commands/tsconfig.json
./node_modules/.bin/tsgo --build pnpm/tsconfig.json
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/runPacquet.ts --runInBand
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/index.ts -t "config dependency code allowlists|user-level preference settings" --runInBand
./node_modules/.bin/eslint config/reader/src/Config.ts config/reader/src/types.ts config/reader/src/configFileKey.ts config/reader/src/index.ts config/reader/test/index.ts installing/commands/src/installDeps.ts installing/commands/test/runPacquet.ts pnpm/test/install/pacquet.ts
git diff --check
```

The full patched replay for the shared branch passed with all 20 candidates marked fixed. This candidate's replay evidence is `results/CAND-PNPM-097-patched-result.json`.
<!-- maintainer-action:end -->

### Summary

pnpm can install `configDependencies` declared in `pnpm-workspace.yaml` before command dispatch. Before the patch, a repository could declare `pacquet` or `@pnpm/pacquet` as a config dependency and pnpm treated that repository-controlled dependency as an install-engine opt-in. During install, pnpm resolved a platform-specific `@pacquet/<platform>-<arch>/pacquet` binary from `node_modules/.pnpm-config/<packageName>` and spawned it as the developer or CI user.

### Details

The vulnerable source-to-sink path was:

- `config/reader/src/getOptionsFromRootManifest.ts` copies repository `pnpm-workspace.yaml` `configDependencies` into config.
- `pnpm/src/getConfig.ts` installs config dependencies before command dispatch.
- `installing/env-installer/src/resolveAndInstallConfigDeps.ts` resolves the repository-declared dependency and its optional platform subdependencies.
- `installing/env-installer/src/installConfigDeps.ts` fetches, imports, and symlinks the config dependency tree under `node_modules/.pnpm-config`.
- `installing/commands/src/installDeps.ts` selected pacquet delegation whenever `configDependencies` contained `pacquet` or `@pnpm/pacquet`.
- `installing/deps-installer/src/install/index.ts` called `opts.runPacquet` from frozen and materialization paths.
- `installing/commands/src/runPacquet.ts` resolved `@pacquet/${process.platform}-${process.arch}/pacquet` from the installed config dependency package and executed it with `spawn()`.

Exact-version, integrity, and platform filters only proved which bytes package resolution selected; they did not establish that the repository was trusted to choose a native install engine.

### PoC

Standalone PoC and verification script:

Repository fixture:

```yaml
packages:
  - .
configDependencies:
  pacquet: 0.2.2
```

Registry package shape:

```json
{
  "name": "pacquet",
  "version": "0.2.2",
  "optionalDependencies": {
    "@pacquet/darwin-arm64": "0.2.2"
  }
}
```

Platform package payload:

```sh
#!/bin/sh
echo "$PWD" > /tmp/pacquet-engine-ran
env > /tmp/pacquet-engine-env
```

Pre-patch exploit model:

1. The victim runs a dependency-management command such as `pnpm install` in the repository.
2. pnpm installs the repository-declared config dependency and its host-compatible optional platform dependency into `.pnpm-config`.
3. `installDeps()` treats the presence of `configDependencies.pacquet` or `configDependencies["@pnpm/pacquet"]` as authorization to delegate install materialization.
4. `runPacquet()` resolves the platform binary from the installed config dependency tree and spawns it in the lockfile directory.

Observed PoC output:

```json
{
  "primitive": "repository-selected pacquet config dependency reaches native process execution when selected",
  "patchedWithoutAllowlist": "blocked",
  "trustedAllowlist": "allows explicit opt-in"
}
```

Focused validation commands:

```bash
./node_modules/.bin/tsgo --build config/reader/tsconfig.json
./node_modules/.bin/tsgo --build installing/commands/tsconfig.json
./node_modules/.bin/tsgo --build pnpm/tsconfig.json
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/runPacquet.ts --runInBand
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/index.ts -t "config dependency code allowlists|user-level preference settings" --runInBand
./node_modules/.bin/eslint config/reader/src/Config.ts config/reader/src/types.ts config/reader/src/configFileKey.ts config/reader/src/index.ts config/reader/test/index.ts installing/commands/src/installDeps.ts installing/commands/test/runPacquet.ts pnpm/test/install/pacquet.ts
git diff --check
```

Validation result:

- The PoC confirmed a selected pacquet config dependency reaches native process execution.
- Patched `getPacquetConfigDependencyName()` returns `undefined` without a trusted allowlist.
- Patched `getPacquetConfigDependencyName()` allows exact `pacquet`, exact `@pnpm/pacquet`, and wildcard `*` trusted opt-in.
- Config reader regressions prove user/global config can set `configDependencyInstallEngineAllowlist`, while `pnpm-workspace.yaml` cannot grant this permission to itself.
- E2E fixtures that intentionally delegate to pacquet now pass the trusted allowlist through environment config.
- TypeScript builds passed for `@pnpm/config.reader`, `@pnpm/installing.commands`, and `pnpm`.
- Focused `installing/commands/test/runPacquet.ts`: 3 passed.
- Focused `config/reader/test/index.ts`: 2 passed, 132 skipped under the focused pattern.
- ESLint passed with warnings only for existing skipped tests in `config/reader/test/index.ts` and `pnpm/test/install/pacquet.ts`.
- `git diff --check`: passed.

### Impact

A malicious repository can cause pnpm to execute a registry-selected native binary while handling dependency-management commands. The binary runs with the victim developer or CI user's filesystem, environment, registry credentials, git/SSH credentials, and network access.

## Affected products

Ecosystem: npm

Package name: `pnpm`, `@pnpm/config.reader`, `@pnpm/installing.commands`

Affected versions: current main before this patch, when `configDependencies` contains `pacquet` or `@pnpm/pacquet` and install paths delegate to pacquet.

Patched versions: 10.34.2, 11.5.3.

## Severity

Severity: High

Vector string: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H`

Base score: 8.8

Rationale: attacker input is delivered through a repository and registry package, exploitation is low complexity once the victim runs pnpm, no attacker privileges are required, and user interaction is required. Successful exploitation executes a native binary in the victim user's context, with high confidentiality, integrity, and availability impact.

## Weaknesses

CWE-829: Inclusion of Functionality from Untrusted Control Sphere

CWE-78: Improper Neutralization of Special Elements used in an OS Command

CWE-494: Download of Code Without Integrity Check

## Patch

The patch adds a trusted opt-in gate for config-dependency install-engine delegation:

- New setting: `configDependencyInstallEngineAllowlist`.
- The allowlist can be set from trusted user-controlled config such as global config, CLI config, or environment config.
- `pnpm-workspace.yaml` cannot grant this permission to itself; workspace-provided values are discarded after workspace settings are merged.
- `installDeps()` delegates to pacquet only when `pacquet`, `@pnpm/pacquet`, or `*` is present in the trusted allowlist.
- Repositories can still install `pacquet` as a config dependency, but pnpm will not spawn it as an install engine unless trusted config opts in.
- Existing tests that intentionally exercise pacquet delegation were updated to pass the trusted allowlist via environment config.

Changed files:

- `config/reader/src/Config.ts`
- `config/reader/src/types.ts`
- `config/reader/src/configFileKey.ts`
- `config/reader/src/index.ts`
- `config/reader/test/index.ts`
- `installing/commands/src/installDeps.ts`
- `installing/commands/test/runPacquet.ts`
- `pnpm/test/install/pacquet.ts`

Changeset:

- `.changeset/lucky-config-plugin-pnpmfiles.md`

Pacquet parity:

No pacquet-side code-execution sink exists for this finding. The Rust port parses and records `configDependencies` for workspace-state compatibility, but it does not install config dependencies or select/spawn an alternate install engine from them. The user-visible trust setting is TypeScript-side today because it gates pnpm's pacquet delegation path.

## CVSS Reassessment

Initial CVSS remains correct for vulnerable versions: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` / 8.8 High.

Final CVSS after patch: not vulnerable after patch / 0.0. The PoC no longer reaches pacquet install-engine selection or native process execution unless the victim has set a trusted allowlist outside the repository's own workspace settings.

## Remaining Risk

Users can explicitly trust pacquet install-engine delegation through the new allowlist. That is intentional behavior; the closed issue is repository self-authorization of a registry-provided native install engine.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-gj8w-mvpf-x27x
- https://nvd.nist.gov/vuln/detail/CVE-2026-55697
- https://github.com/pnpm/pnpm
