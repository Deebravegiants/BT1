# [M] Setup PHP: GitHub tokens configured by setup-php may be exposed through pinned affected Composer versions

## Summary
Severity: Medium
Advisory: GHSA-5wxr-w449-57cm
CWE: CWE-532
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-20
Source: https://github.com/advisories/GHSA-5wxr-w449-57cm
Type: github-advisory

## Affected
- GitHub Actions: `shivammathur/setup-php` — affected >=0 <2.37.1

## Details
### Impact
This affects only workflows that pin an exact affected Composer semver version through setup-php, for example `tools: composer:2.9.7`.

Workflows using the default Composer version, `composer:v2`, or no pinned Composer version are not affected through setup-php, because those Composer URLs have been updated to patched Composer releases for all setup-php versions.

setup-php does not directly print the token. The token may be exposed through Composer when Composer validates github-oauth auth and rejects GitHub's newer hyphen-containing token format.

Public repository logs may expose the token. GitHub-hosted runner GITHUB_TOKEN values expire after the job, but exposure may still matter during the token lifetime and for longer-lived GitHub App or user tokens.

### Patches
setup-php 2.37.1 skips generated GitHub OAuth auth for pinned Composer versions affected by Composer GHSA-f9f8-rm49-7jv2 while preserving other Composer auth, including Packagist auth.

### Workarounds
Upgrade to setup-php `2.37.1` or newer. You can also avoid the affected path by using a patched Composer version: 2.9.8, 2.2.28, 1.10.28, or newer supported Composer releases.

It is recommended to avoid pinning affected Composer versions such as `composer:2.9.7`, unless you have automations to do timely updates in your workflows.

## References
- https://github.com/composer/composer/security/advisories/GHSA-f9f8-rm49-7jv2
- https://github.com/shivammathur/setup-php/security/advisories/GHSA-5wxr-w449-57cm
- https://github.com/shivammathur/setup-php/commit/7748c243803a56671412f9f7c745769e9573c6d4
- https://github.com/shivammathur/setup-php
