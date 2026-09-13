# [H] Helm has a path traversal in plugin metadata version enables arbitrary file write outside Helm plugin directory

## Summary
Severity: High
Advisory: GHSA-vmx8-mqv2-9gmg
CVE: CVE-2026-35204
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-vmx8-mqv2-9gmg
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v4` — affected >=4.0.0 <4.1.4

## Details
Helm is a package manager for Charts for Kubernetes. In Helm versions >=4.0.0 and <=4.1.3, a specially crafted Helm plugin, when installed or updated, will cause Helm to write the contents of the plugin to an arbitrary filesystem location.

### Impact

A Helm user who installs or updates a plugin that is specially crafted can cause Helm to attempt to write the content of the affected plugin to an arbitrary location on the user's filesystem. Impacted users risk potentially overwriting user and system files which may further compromise the integrity of a system.

### Patches

This issue has been patched in Helm v4.1.4

Installing/updating a plugin with a non-SemVer version (which excludes path traversal patterns) will result in an error.

### Workarounds

Validate that the `plugin.yaml` of the Helm plugin does not include a `version:` field containing POSIX dot-dot path separators ie. "`/../`".

## References
- https://github.com/helm/helm/security/advisories/GHSA-vmx8-mqv2-9gmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35204
- https://github.com/helm/helm/commit/36c8539e99bc42d7aef9b87d136254662d04f027
- https://github.com/helm/helm
- https://github.com/helm/helm/releases/tag/v4.1.4
