# [H] Helm's plugin verification fails open when .prov is missing, allowing unsigned plugin install

## Summary
Severity: High
Advisory: GHSA-q5jf-9vfq-h4h7
CVE: CVE-2026-35205
CWE: CWE-636
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-q5jf-9vfq-h4h7
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v4` — affected >=4.0.0 <4.1.4

## Details
Helm is a package manager for Charts for Kubernetes. In Helm versions >=4.0.0 and <=4.1.3, Helm will install plugins missing provenance (`.prov` file) when signature verification is required.

### Impact

The bug allows plugin authors to omit provenance (signing) data from plugins, bypassing plugin signature verification upon plugin install/update.

Notably, plugin hooks will be executed as designed on the installed plugin, enabling a malicious plugin to execute arbitrary code.

### Patches

This issue has been patched in Helm v4.1.4

Installing/updating a plugin with missing provenance will error if signature verification is required.

### Workarounds

Users may manually validate that a plugin archive is not missing provenance data (`.prov` file) before installation.

## References
- https://github.com/helm/helm/security/advisories/GHSA-q5jf-9vfq-h4h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35205
- https://github.com/helm/helm/commit/05fa37973dc9e42b76e1d2883494c87174b6074f
- https://github.com/helm/helm
- https://github.com/helm/helm/releases/tag/v4.1.4
- https://helm.sh/docs/topics/provenance/#the-provenance-file
