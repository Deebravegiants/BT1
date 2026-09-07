# [M] nono-cli'scregistry pack verification can fail open when provenance metadata is absent

## Summary
Severity: Medium
Advisory: GHSA-hc4m-q9jh-xw4j
CWE: CWE-636
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-hc4m-q9jh-xw4j
Type: github-advisory

## Affected
- crates.io: `nono-cli` — affected >=0 <0.61.3

## Details
## Summary

Registry-installed nono packs are expected to be verified from local provenance metadata before they are used. Two files are relevant:

- `~/.config/nono/packages/lockfile.json`
- `~/.config/nono/packages/<namespace>/<pack>/.nono-trust.bundle`

Testing shows that nono fails closed when a pack has a trust bundle but no lockfile entry. However, if the trust bundle is also absent, the same pack can load successfully. Deleting security metadata should not make a pack easier to run.

## Affected behavior

Observed with `always-further/claude`:

1. Delete `~/.config/nono/packages/lockfile.json`.

   Result:

   ```text
   nono: Package verification failed for always-further/claude: pack 'always-further/claude' has a trust bundle but no lockfile entry - reinstall with: nono pull always-further/claude --force
   ```

2. Delete `~/.config/nono/packages/always-further/claude/.nono-trust.bundle`.

   Result: the profile loads successfully.

3. Restore `.nono-trust.bundle` while the lockfile is still absent.

   Result:

   ```text
   nono: Package verification failed for always-further/claude: pack 'always-further/claude' has a trust bundle but no lockfile entry - reinstall with: nono pull always-further/claude --force
   ```

## Impact

If both the lockfile entry and trust bundle are absent, nono may accept an installed registry pack without artifact hash verification or provenance verification.

This is especially important for pack-provided session hooks, because session hooks execute on the host outside the sandbox. A pack that contributes host-executed code should not run unless nono can verify that the code is a locked and trusted pack artifact.

## Root cause

`verify_profile_packs` treats the lockfile entry as optional. Existing code fails when a trust bundle exists without a matching lockfile entry, but when the trust bundle is absent too, there is no equivalent hard failure.

That creates a fail-open state:

- lockfile entry missing
- trust bundle missing
- pack directory still present
- profile can load

## Recommended fix

For any registry pack selected for execution, require both:

1. A matching lockfile entry in `~/.config/nono/packages/lockfile.json`.
2. A present and valid `.nono-trust.bundle` in the installed pack directory.

If either is missing, fail closed with a reinstall instruction, for example:

```text
reinstall with: nono pull <namespace>/<pack> --force
```

This keeps verification monotonic: removing provenance metadata cannot downgrade a verification failure into a successful launch.

## References
- https://github.com/always-further/nono/security/advisories/GHSA-hc4m-q9jh-xw4j
- https://github.com/nolabs-ai/nono/commit/db07375031642f089d549b4f7b9abece87e39f87
- https://github.com/always-further/nono
- https://github.com/nolabs-ai/nono/releases/tag/v0.62.0
