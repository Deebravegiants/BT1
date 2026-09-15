# [M] Renovate affected by remote code execution was possible using the bazel-module or bazelisk managers, when using lockFileMaintenance

## Summary
Severity: Medium
Advisory: GHSA-5vjq-5jmg-39xq
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-5vjq-5jmg-39xq
Type: github-advisory

## Affected
- npm: `renovate` — affected >=43.65.0 <43.102.11

## Details
When using [`lockFileMaintenance`](https://docs.renovatebot.com/configuration-options/#lockfilemaintenance) using the [bazel-module](https://docs.renovatebot.com/modules/manager/bazel-module/) or [bazelisk](https://docs.renovatebot.com/modules/manager/bazelisk/) managers between Renovate [43.65.0](https://github.com/renovatebot/renovate/releases/tag/43.65.0) (2026-03-12) and [43.102.11](https://github.com/renovatebot/renovate/releases/tag/43.102.11) (2026-04-02), there was the opportunity for remote code execution from a malicious dependency, _if the Bazel module executes code that relies on a dependency_.

As this is an "unsafe" execution path, we have disabled this by default, and self-hosted administrators must add it to the [`allowedUnsafeExecutions`](https://docs.renovatebot.com/self-hosted-configuration/#allowedunsafeexecutions) allowlist.

It is recommended to review whether you have enabled this functionality for these managers, and if so, whether any dependency updates may have led to remote code execution.

## Impact

If Renovate suggested an update to a malicious dependency, _and_ that dependency is referenced as part of the `bazel mod deps` call - for instance as part of a `ctx.execute` call - this would call attacker-controlled code.

This could lead to [insider attackers](https://docs.renovatebot.com/security-and-permissions/#execution-of-code-insider-attack) and [outside attackers](https://docs.renovatebot.com/security-and-permissions/#execution-of-code-outsider-attack), executing code that is distributed as part of the package.
 
## Patches

This is patched in [43.102.11](https://github.com/renovatebot/renovate/releases/tag/43.102.11).

This does not affect any versions of [Mend Renovate Self-Hosted](https://www.mend.io/renovate/).

## Workarounds

- Upgrade your Renovate version
- Disable `lockFileMaintenance` for these managers

## Why did this happen?

This was missed in code review (as part of https://github.com/renovatebot/renovate/pull/41507).

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-5vjq-5jmg-39xq
- https://github.com/renovatebot/renovate
- https://github.com/renovatebot/renovate/releases/tag/43.102.11
