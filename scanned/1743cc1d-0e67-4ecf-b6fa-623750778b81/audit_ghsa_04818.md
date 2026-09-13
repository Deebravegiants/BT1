# [M] pnpm: Unsafe default behavior breaks integrity check

## Summary
Severity: Medium
Advisory: GHSA-54hh-g5mx-jqcp
CVE: CVE-2026-50573
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-54hh-g5mx-jqcp
Type: github-advisory

## Affected
- npm: `pnpm` — affected >=0 <10.34.0
- npm: `pnpm` — affected >=11.0.0 <11.4.0

## Details
While it is unclear whether this should be classified as a vulnerability, it is being reported through this channel because the current behavior may represent an unsafe default.

## Summary

`pnpm install` in non-frozen mode can accept new remote package content after detecting that the downloaded tarball does not match the integrity recorded in `pnpm-lock.yaml`.

When a package is already locked with an `integrity` value, and the registry later serves different metadata and tarball content for the same package name and version, pnpm initially reports an integrity mismatch. However, plain `pnpm install` then performs a resolution repair, accepts the registry's new integrity, updates the lockfile, installs the new content, and exits successfully.

This means the lockfile integrity check does not act as a hard stop by default.

## Reproduction Scenario

1. Run a local npm-compatible registry.
2. Publish or serve `example-package@1.0.0` with tarball content `v1`.
3. Install it with pnpm:

```bash
pnpm add example-package@1.0.0 --registry=http://127.0.0.1:48741
```

4. Confirm `pnpm-lock.yaml` contains the `v1` integrity:

```yaml
packages:
  example-package@1.0.0:
    resolution:
      integrity: sha512-...v1...
```

5. Change the registry metadata and tarball for the same `example-package@1.0.0` to content `v2`.
6. On a clean store/cache, run:

```bash
pnpm install --registry=http://127.0.0.1:48741
```

## Observed Behavior

pnpm detects the checksum mismatch:

```text
WARN Got unexpected checksum for "http://127.0.0.1:48741/example-package/-/example-package-1.0.0.tgz".
Wanted "sha512-...v1..."
Got "sha512-...v2...".

ERR_PNPM_TARBALL_INTEGRITY The lockfile is broken! Resolution step will be performed to fix it.
```

However, the install still succeeds:

```text
INSTALL_RC=0
INSTALLED=v2-replaced
```

The lockfile is then rewritten to trust the new remote integrity:

```yaml
packages:
  example-package@1.0.0:
    resolution:
      integrity: sha512-...v2...
```

## Expected Behavior

If a downloaded tarball does not match the integrity recorded in `pnpm-lock.yaml`, the install should fail by default.

The lockfile integrity should be treated as authoritative unless the user explicitly requests lockfile repair or dependency update behavior.

## Security Impact

This behavior weakens the protection normally expected from a committed lockfile.

If a registry is compromised and an attacker overwrites the metadata and tarball for an existing package version, a new environment without the old pnpm store/cache may install the attacker's replacement package even though the project already has a lockfile with the original integrity.

Examples of affected new or clean environments include:

- an engineer setting up the project on a new machine
- a new team member onboarding to the project

In this situation, pnpm first detects that the downloaded tarball does not match the integrity stored in `pnpm-lock.yaml`. However, instead of failing by default, plain `pnpm install` performs a resolution repair, trusts the current remote registry metadata, updates the lockfile to the new integrity, and installs the new registry content.

In other words, when the lockfile and registry disagree, the default non-frozen behavior can end up trusting the remote registry over the content previously recorded in the lockfile.

This is especially relevant for:

- private registries that allow overwriting or republishing the same version
- registry mirrors or proxies that can serve changed metadata and tarballs
- compromised public or private registries
- compromised registry proxy infrastructure

The behavior is also surprising because the command reports an integrity error but still exits successfully after resolution repair.

This issue does not occur when `--frozen-lockfile` is enabled. In frozen mode, the same integrity mismatch fails the install and does not install the changed package content.

However, since the lockfile already records an integrity value, the integrity for the same package version should normally not change. If it does change, one likely explanation is that the server or registry has been compromised or is serving mutated package content. Under normal package publishing workflows, changed package content should be published as a new version instead of replacing an existing version.

For that reason, it may be safer for pnpm's default behavior to be closer to frozen mode for this specific case. At minimum, pnpm should not automatically repair the lockfile and trust the registry after an integrity mismatch. It should fail and let the user explicitly decide whether to discard the locked integrity, re-resolve the package from the remote registry, and update the lockfile.

## Comparison

In the same scenario, `npm install` with an existing `package-lock.json` fails with `EINTEGRITY` and does not install the changed tarball.

`pnpm install --frozen-lockfile` also fails as expected:

```text
ERR_PNPM_TARBALL_INTEGRITY
```

The issue is specific to the default non-frozen behavior of plain `pnpm install` in non-CI environment.

## References
- https://github.com/pnpm/pnpm/security/advisories/GHSA-54hh-g5mx-jqcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-50573
- https://github.com/pnpm/pnpm
