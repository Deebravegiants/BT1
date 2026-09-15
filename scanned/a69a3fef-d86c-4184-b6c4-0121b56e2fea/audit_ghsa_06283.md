# [M] Trivy Plugin Manager has Path Traversal that Allows Arbitrary File Write

## Summary
Severity: Medium
Advisory: GHSA-8rc5-4fr6-64pw
CVE: CVE-2026-63328
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-8rc5-4fr6-64pw
Type: github-advisory

## Affected
- Go: `github.com/aquasecurity/trivy` — affected >=0 <0.72.0

## Details
## Summary

Trivy's plugin manager does not fully validate metadata from a plugin's manifest before using it to construct filesystem paths under the plugin root (`~/.trivy/plugins`). A crafted plugin can cause Trivy to write its files (the manifest and the downloaded plugin binary) outside the plugin root, to an arbitrary location writable by the user running Trivy.

Plugins are third-party binaries that Trivy downloads and executes, so Trivy's [documentation](https://trivy.dev/docs/latest/guide/plugin/) already advises installing only plugins you trust. This issue does not change that trust boundary: exploitation requires the user to install a malicious plugin in the first place.

## Affected configurations

The vulnerability is triggered only when a user installs an attacker-controlled plugin, for example via `trivy plugin install <SOURCE>` or `trivy plugin run <SOURCE>`. An attacker has to trick a user into installing a plugin they crafted, for instance by publishing it or by getting a malicious source pasted into a command or documentation snippet.

Plugins distributed through the official Trivy plugin index are not affected.

## Impact

A user who installs a malicious plugin can have files written outside the plugin root, to any location writable by the user running Trivy. The vulnerability does not grant any privileges beyond what that user already has.

## Patches

Fixed in Trivy `0.72.0`. Users should upgrade to that release or later.

## Workarounds

Only install Trivy plugins from sources you trust. Plugins from the official Trivy plugin index are safe. See the [plugin documentation](https://trivy.dev/docs/latest/guide/plugin/) for details.

## Credits

Reported by @fatihhcelik.

## References
- https://github.com/aquasecurity/trivy/security/advisories/GHSA-8rc5-4fr6-64pw
- https://github.com/aquasecurity/trivy/commit/d4213d7735c74e57f06c02ccb39ebca67abc7959
- https://github.com/aquasecurity/trivy
- https://github.com/aquasecurity/trivy/releases/tag/v0.72.0
