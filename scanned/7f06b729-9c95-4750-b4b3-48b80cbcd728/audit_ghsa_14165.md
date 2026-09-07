# [M] Tauri Open Redirect Vulnerability Possibly Exposes IPC to External Sites

## Summary
Severity: Medium
Advisory: GHSA-4wm2-cwcf-wwvp
CVE: CVE-2023-31134
CWE: CWE-601
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-03
Source: https://github.com/advisories/GHSA-4wm2-cwcf-wwvp
Type: github-advisory

## Affected
- crates.io: `tauri` — affected >=1.0.0 <1.0.9
- crates.io: `tauri` — affected >=1.1.0 <1.1.4
- crates.io: `tauri` — affected >=1.2.0 <1.2.5

## Details
### Impact
The Tauri IPC is usually strictly isolated from external websites but the isolation can be bypassed by redirecting an existing Tauri window to an external website. This is either possible by an application implementing a feature for users to visit arbitrary websites or due to a bug allowing the open redirect[^open-redirect].

This allows the external website access to the IPC layer and therefore to all configured and exposed Tauri API endpoints and application specific implemented Tauri commands.

### Patches
This issue has been patched in the latest release and was backported to all previous `1.x` releases.

### Workarounds
Prevent arbitrary input in redirect features. Only allow trusted websites access to the IPC.

### References

The feature to enable this behavior in a more constrained way was introduced in the `1.3` release and documentation around this can be found in the [documentation](https://tauri.app/v1/api/config/#securityconfig.dangerousremotedomainipcaccess).

[^open-redirect]: [https://en.wikipedia.org/wiki/Open_redirect](https://en.wikipedia.org/wiki/Open_redirect)

## References
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-4wm2-cwcf-wwvp
- https://nvd.nist.gov/vuln/detail/CVE-2023-31134
- https://github.com/tauri-apps/tauri/commit/9c0593c33af52cd9e00ec784d15f63efebdf039c
- https://en.wikipedia.org/wiki/Open_redirect
- https://github.com/tauri-apps/tauri
- https://github.com/tauri-apps/tauri/releases/tag/tauri-v1.0.9
- https://github.com/tauri-apps/tauri/releases/tag/tauri-v1.1.4
- https://github.com/tauri-apps/tauri/releases/tag/tauri-v1.2.5
- https://tauri.app/v1/api/config/#securityconfig.dangerousremotedomainipcaccess
- https://www.github.com/tauri-apps/tauri/commit/58ea0b45268dbd46cbac0ebb0887353d057ca767
- https://www.github.com/tauri-apps/tauri/commit/fa90214b052b1a5d38d54fbf1ca422b4c37cfd1f
