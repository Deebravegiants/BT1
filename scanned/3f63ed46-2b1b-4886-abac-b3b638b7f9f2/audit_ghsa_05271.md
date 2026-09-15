# [H] pnpm: Project env lockfile can short-circuit package-manager resolution and execute lockfile-selected pnpm bytes

## Summary
Severity: High
Advisory: GHSA-w466-c33r-3gjp
CVE: CVE-2026-55698
CWE: CWE-345, CWE-494, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-w466-c33r-3gjp
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.2
- npm: `pnpm` — affected >=11.0.0 <11.5.3

## Details
<!-- maintainer-action:start -->
## Maintainer Action Plan

This report is ready to review with the shared patch branch. Start with the PR and the expected fixed behavior, then use the detailed exploit narrative below only if you want to replay the original path.

- Advisory: `CAND-PNPM-063` / `GHSA-w466-c33r-3gjp`
- Advisory URL: https://github.com/pnpm/pnpm/security/advisories/GHSA-w466-c33r-3gjp
- Shared patch PR: https://github.com/pnpm/pnpm-ghsa-j2hc-m6cf-6jm8/pull/1
- Shared patch branch: `security/ghsa-batch-2026-06-09`
- Patch commit: `a93449314f398cf4bdf2e28d033c02d37395ad22`
- Base commit: `origin/main` `55a4035abf1ae3fe7208ba1f5ef43c5eff58ccec`
- Maintainer priority: `start-here`
- Component: `pnpm packageManager env lockfile`
- Patch area: package-manager env lockfile is re-resolved through trusted registries before execution
- Affected packages: `npm:pnpm`, `npm:@pnpm/installing.env-installer`
- CWE IDs: `CWE-829`, `CWE-494`, `CWE-345`
- Conservative CVSS: `8.8` / `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H`
- Next action: review the shared patch branch for this component, set the final affected version range, merge and release the fix, then publish or close the advisory.

### Expected Patched Behavior

Committed env-lockfile package-manager entries are force-refreshed through trusted registries before execution; attacker tarball requests and markers stay at zero.

### Files And Tests To Review

- `installing/env-installer/src/resolvePackageManagerIntegrities.ts`
- `pnpm/src/switchCliVersion.ts`
- `pnpm/src/switchCliVersion.test.ts`
- `.changeset/clean-package-manager-registries.md`

### Focused Validation

Run these from a checkout of the shared patch branch. They are the useful maintainer commands with machine-local artifact paths removed.

```bash
./node_modules/.bin/tsgo --build installing/env-installer/tsconfig.json
./node_modules/.bin/tsgo --build pnpm/tsconfig.json
PNPM_REGISTRY_MOCK_PORT=7799 NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../node_modules/.bin/jest src/switchCliVersion.test.ts -t "re-resolved package-manager lockfile" --runInBand
PNPM_REGISTRY_MOCK_PORT=7799 NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../node_modules/.bin/jest src/switchCliVersion.test.ts src/syncEnvLockfile.test.ts --runInBand
./node_modules/.bin/eslint installing/env-installer/src/resolvePackageManagerIntegrities.ts pnpm/src/switchCliVersion.ts pnpm/src/switchCliVersion.test.ts
git diff --check
```

The full patched replay for the shared branch passed with all 20 candidates marked fixed. This candidate's replay evidence is `results/CAND-PNPM-063-patched-result.json`.
<!-- maintainer-action:end -->

### Summary

pnpm can persist package-manager bootstrap metadata in the first YAML document of `pnpm-lock.yaml`. Before the patch, direct pnpm execution trusted an already resolved `packageManagerDependencies` entry when the committed env lockfile contained matching `pnpm` and `@pnpm/exe` versions. A malicious repository could therefore commit package-manager lockfile package records and snapshots that bypassed fresh package-manager resolution, then cause pnpm to install and execute bytes selected by that committed lockfile state during automatic version switching.

### Details

The vulnerable source-to-sink path was:

- `lockfile/fs/src/envLockfile.ts` reads the repository's first YAML lockfile document and validates shape only.
- `pnpm/src/main.ts` reaches `switchCliVersion()` when a direct pnpm invocation sees a wanted `pnpm` package manager with `onFail=download`.
- `pnpm/src/switchCliVersion.ts` reads the committed env lockfile when package-manager metadata should be persisted.
- `installing/env-installer/src/resolvePackageManagerIntegrities.ts` treated `packageManagerDependencies` as resolved when only the `pnpm` and `@pnpm/exe` versions matched.
- `engine/pm/commands/src/self-updater/installPnpm.ts` converts env-lockfile `snapshots` and `packages` into the wanted lockfile used by `headlessInstall()`.
- `pnpm/src/switchCliVersion.ts` executes the installed `pnpm` binary with `spawn.sync()`.

The helper fast path is intentionally still version-based for non-execution callers, so the security boundary is enforced at the execution path: `switchCliVersion()` now re-resolves already present package-manager env-lockfile entries before they can reach `installPnpmToStore()` and `spawn.sync()`.

### PoC

Standalone PoC and verification script:

The PoC constructs a committed env-lockfile object with matching package-manager dependency versions and attacker-selected package metadata:

```json
{
  "importers": {
    ".": {
      "configDependencies": {},
      "packageManagerDependencies": {
        "@pnpm/exe": { "specifier": "9.3.0", "version": "9.3.0" },
        "pnpm": { "specifier": "9.3.0", "version": "9.3.0" }
      }
    }
  },
  "lockfileVersion": "9.0",
  "packages": {
    "/pnpm@9.3.0": {
      "resolution": {
        "integrity": "sha512-poisoned"
      }
    }
  },
  "snapshots": {
    "/pnpm@9.3.0": {}
  }
}
```

Pre-patch exploit model:

1. The victim runs pnpm directly in a malicious repository.
2. The requested package-manager version differs from the currently running pnpm.
3. pnpm enters `switchCliVersion()` and reads the committed env lockfile.
4. Matching `pnpm` / `@pnpm/exe` versions short-circuit package-manager resolution.
5. pnpm installs from the committed env-lockfile package records and executes the resulting `pnpm` binary.

Observed primitive proof from the PoC:

```json
{
  "primitive": "unforced resolver reuses already-resolved env lockfile metadata",
  "isResolvedByVersionOnly": true,
  "reusedPoisonedIntegrity": true
}
```

The same script then runs the patched `switchCliVersion` regression. The regression seeds a poisoned committed env lockfile, has the resolver return a trusted replacement lockfile, and asserts `installPnpmToStore()` receives the trusted lockfile rather than the committed one. This would fail on the vulnerable control flow because the resolver was not called and the committed lockfile reached the installer.

Focused validation commands:

```bash
./node_modules/.bin/tsgo --build installing/env-installer/tsconfig.json
./node_modules/.bin/tsgo --build pnpm/tsconfig.json
PNPM_REGISTRY_MOCK_PORT=7799 NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../node_modules/.bin/jest src/switchCliVersion.test.ts -t "re-resolved package-manager lockfile" --runInBand
PNPM_REGISTRY_MOCK_PORT=7799 NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../node_modules/.bin/jest src/switchCliVersion.test.ts src/syncEnvLockfile.test.ts --runInBand
./node_modules/.bin/eslint installing/env-installer/src/resolvePackageManagerIntegrities.ts pnpm/src/switchCliVersion.ts pnpm/src/switchCliVersion.test.ts
git diff --check
```

Validation result:

- The PoC confirmed the unforced resolver still reuses a version-matching env lockfile, proving the original primitive.
- Patched `switchCliVersion()` calls `resolvePackageManagerIntegrities()` with `force: true` when committed env-lockfile package-manager entries already satisfy the requested version.
- Patched `switchCliVersion()` assigns the resolver return value back to `envLockfile`.
- The installer receives the refreshed lockfile and not the poisoned committed lockfile.
- TypeScript builds passed for `@pnpm/installing.env-installer` and `pnpm`.
- The focused Jest regression passed: 1 passed, 1 skipped in `switchCliVersion.test.ts`.
- ESLint passed for the affected package-manager switch files.
- `git diff --check` passed.

### Impact

A malicious repository can cause arbitrary package-manager code execution in the victim's developer or CI environment before normal command handling continues. That code executes with the victim user's privileges and can read local secrets, alter project files, mutate dependency state, or run further commands.

## Affected products

Ecosystem: npm

Package name: `pnpm`, `@pnpm/installing.env-installer`

Affected versions: current main before this patch; direct pnpm execution with package-manager auto-switching and a repository-controlled env lockfile.

Patched versions: pending release containing this patch.

## Severity

Severity: High

Vector string: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H`

Base score: 8.8

Rationale: the malicious source is repository-controlled package-manager lockfile state delivered through normal supply-chain channels. Exploitation is low complexity once the victim runs pnpm directly, no attacker privileges are required, and user interaction is required. Successful exploitation executes attacker-selected package-manager code in the victim user's security context, with high confidentiality, integrity, and availability impact.

## Weaknesses

CWE-829: Inclusion of Functionality from Untrusted Control Sphere

CWE-494: Download of Code Without Integrity Check

CWE-345: Insufficient Verification of Data Authenticity

## Patch

The patch makes automatic package-manager switching re-resolve repository-provided bootstrap metadata before install and execution:

- `resolvePackageManagerIntegrities()` accepts `force`, which bypasses the version-only fast path.
- `switchCliVersion()` creates a store controller even when the committed env lockfile already contains satisfying package-manager dependency versions.
- `switchCliVersion()` calls `resolvePackageManagerIntegrities()` with `force: true` for already resolved package-manager entries.
- `switchCliVersion()` assigns the returned env lockfile back to `envLockfile`, so `installPnpmToStore()` installs from freshly resolved metadata.
- The package-manager bootstrap registry hardening from CAND-PNPM-061 is reused, so the refresh happens through trusted package-manager registries rather than repository workspace registries.

Changed files:

- `installing/env-installer/src/resolvePackageManagerIntegrities.ts`
- `pnpm/src/switchCliVersion.ts`
- `pnpm/src/switchCliVersion.test.ts`

Changeset:

- `.changeset/clean-package-manager-registries.md`

Pacquet parity:

No pacquet-side patch is required for this finding because pacquet does not implement pnpm's package-manager auto-switch path or `installPnpmToStore()`.

## CVSS Reassessment

Initial CVSS remains correct for vulnerable versions: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` / 8.8 High.

Final CVSS after patch: not vulnerable after patch / 0.0. The PoC still demonstrates the underlying unforced env-lockfile reuse primitive, but the patched execution path force-refreshes package-manager metadata through trusted bootstrap registries before install or execution.

## Remaining Risk

The helper `resolvePackageManagerIntegrities()` still has an unforced fast path that treats matching `pnpm` and `@pnpm/exe` versions as resolved. Current execution-sensitive callers either use trusted roots/registries or pass through the patched `switchCliVersion()` boundary, but future execution paths should use `force: true` before installing or executing package-manager bytes from repository-provided env-lockfile metadata.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-w466-c33r-3gjp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55698
- https://github.com/pnpm/pnpm
