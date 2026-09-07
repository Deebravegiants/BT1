# [M] Child processes spawned by Renovate incorrectly have full access to environment variables

## Summary
Severity: Medium
Advisory: GHSA-8wc6-vgrq-x6cf
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-8wc6-vgrq-x6cf
Type: github-advisory

## Affected
- npm: `renovate` — affected >=42.68.1 <42.96.3
- npm: `renovate` — affected >=43.0.0 <43.4.4

## Details
When Renovate spawns child processes, their access to environment variables is filtered to an allowlist, to prevent unauthorized access to privileged credentials that the Renovate process has access to.

Since [42.68.1](https://github.com/renovatebot/renovate/releases/tag/42.68.1) (2025-12-30), this filtering had been **inadvertently removed**, and so any child processes spawned from these versions will have had access to any environment variables that Renovate has access to.

This could lead to [insider attackers](https://docs.renovatebot.com/security-and-permissions/#execution-of-code-insider-attack) and [outside attackers](https://docs.renovatebot.com/security-and-permissions/#execution-of-code-outsider-attack) being able to exflitrate secrets from the Renovate deployment.

It is recommended to rotate (+ revoke) any credentials that Renovate has access to, in case any spawned child processes have attempted to exfiltrate any secrets.

## Impact

Child processes spawned by Renovate (i.e. `npm install`, anything defined in [`postUpgradeTasks`](https://docs.renovatebot.com/configuration-options/#postupgradetasks) or [`postUpdateOptions`](https://docs.renovatebot.com/configuration-options/#postupdateoptions)) will have full access to the environment variables that the Renovate process has. 

This could lead to [insider attackers](https://docs.renovatebot.com/security-and-permissions/#execution-of-code-insider-attack) and [outside attackers](https://docs.renovatebot.com/security-and-permissions/#execution-of-code-outsider-attack) being able to exflitrate secrets from the Renovate deployment.

## Patches

This is patched in [42.96.3](https://github.com/renovatebot/renovate/releases/tag/42.96.3) and [43.4.4](https://github.com/renovatebot/renovate/releases/tag/43.4.4).

## Workarounds

There are no workarounds, other than upgrading your Renovate version.

## Why did this happen?

As part of work towards https://github.com/renovatebot/renovate/security/advisories/GHSA-pfq2-hh62-7m96, one of the [preparatory changes](https://github.com/renovatebot/renovate/pull/40212) we made was moving to [`execa`](https://www.npmjs.com/package/execa).

One of the default behaviours of `execa` is to [extend the process' environment variables with any new ones](https://github.com/sindresorhus/execa/tree/v8.0.1?tab=readme-ov-file#extendenv), rather than override them.

This was missed in code review, which meant that since this version, the full environment variables have been provided to any child processes spawned with `execa` by Renovate.

This was discovered as part of an unrelated change.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-8wc6-vgrq-x6cf
- https://github.com/renovatebot/renovate
- https://github.com/renovatebot/renovate/releases/tag/42.96.3
- https://github.com/renovatebot/renovate/releases/tag/43.4.4
