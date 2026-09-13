# [M] @axonflow/openclaw fix introduces plugin cache and credential-file permission hardening

## Summary
Severity: Medium
Advisory: GHSA-cqmh-pcgr-q42f
CWE: CWE-552, CWE-732
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-cqmh-pcgr-q42f
Type: github-advisory

## Affected
- npm: `@axonflow/openclaw` — affected >=0 <2.0.0

## Details
## Summary

Two related permission defects in this AxonFlow plugin allowed registration credentials and cache state to be readable by other local users on hosts where the calling user's home directory was at the conventional `0755` mode.

## Affected versions

Versions 1.3.2 and below.

## Impact

1. **Cache and config directory mode.** The plugin's directories under `~/.config/axonflow/` and `~/.cache/axonflow/` were created with the umask-derived default mode (often `0755`) on first use and not subsequently re-validated. On systems where `~/.config/` is itself `0755`, the plugin's registration record (including a hashed credential and `instance_id`) was traversable by other local users.
2. **Credential file mode at load time.** The plugin loaded its `try-registration.json` credential file without validating that the file mode was `0600`. A registration file written by a misconfigured tool, copied across systems, or restored from backup could end up world-readable, and the plugin would silently use it.

The fix restores `0700` on all plugin directories on every plugin invocation (not only first creation) and refuses to load credential files with non-`0600` modes.

## Remediation

Upgrade to the patched plugin version listed under Vulnerabilities. On startup the plugin will repair existing directory modes; existing credential files with overly permissive modes will be refused, requiring the user to re-register or `chmod 0600` the file.

## Credit

Identified by AxonFlow internal security review.

## References
- https://github.com/getaxonflow/axonflow-openclaw-plugin/security/advisories/GHSA-cqmh-pcgr-q42f
- https://github.com/getaxonflow/axonflow-openclaw-plugin
