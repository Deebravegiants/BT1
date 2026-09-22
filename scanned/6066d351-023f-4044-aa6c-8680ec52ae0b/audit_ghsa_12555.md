# [M] Tauri vulnerable to Regression on Filesystem Scope Checks for Dotfiles

## Summary
Severity: Medium
Advisory: GHSA-wmff-grcw-jcfm
CVE: CVE-2023-34460
CWE: CWE-285
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-21
Source: https://github.com/advisories/GHSA-wmff-grcw-jcfm
Type: github-advisory

## Affected
- crates.io: `tauri` — affected >=1.4.0 <1.4.1

## Details
### Impact
The 1.4.0 release includes a regression on the filesystem scope check for dotfiles on Linux and macOS.

Previously dotfiles (eg. `$HOME/.ssh/`) were not implicitly allowed by the glob wildcard scopes (eg. `$HOME/*`), but a regression was introduced when a configuration option for this behavior was implemented and dotfiles were implicitly allowed.

Only Tauri applications using wildcard scopes in the `fs` endpoint are affected.
Only macOS and Linux systems are affected.

### Patches
The regression has been patched on `v1.4.1`.

### Workarounds
There are no known workarounds at this time, users should update to `v1.4.1` immediately.

### References
See the [original advisory](https://github.com/tauri-apps/tauri/security/advisories/GHSA-6mv3-wm7j-h4w5) for more information.

### For more Information
If you have any questions or comments about this advisory:

Open an issue in tauri
Email us at [security@tauri.app](mailto:security@tauri.app)

## References
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-6mv3-wm7j-h4w5
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-wmff-grcw-jcfm
- https://nvd.nist.gov/vuln/detail/CVE-2023-34460
- https://github.com/tauri-apps/tauri/pull/6969#discussion_r1232018347
- https://github.com/tauri-apps/tauri/pull/7227
- https://github.com/tauri-apps/tauri/commit/066c09a6ea06f42f550d090715e06beb65cd5564
- https://github.com/tauri-apps/tauri
