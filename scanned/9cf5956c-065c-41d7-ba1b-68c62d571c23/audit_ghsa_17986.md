# [H] Traefik Client Plugin's Path Traversal Vulnerability Allows Arbitrary File Overwrite and Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-q6gg-9f92-r9wg
CVE: CVE-2025-54386
CWE: CWE-22, CWE-30
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-q6gg-9f92-r9wg
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.28
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.4.5
- Go: `github.com/traefik/traefik/v3` — affected >=3.5.0-rc1 <3.5.0

## Details
### Summary
A path traversal vulnerability was discovered in WASM Traefik’s plugin installation mechanism. By supplying a maliciously crafted ZIP archive containing file paths with `../` sequences, an attacker can overwrite arbitrary files on the system outside of the intended plugin directory. This can lead to remote code execution (RCE), privilege escalation, persistence, or denial of service.
 **✅ After investigation, it is confirmed that no plugins on the [Catalog](https://plugins.traefik.io/plugins) were affected. There is no known impact.**

### Details
The vulnerability resides in the WASM plugin extraction logic, specifically in the `unzipFile` function (`/plugins/client.go`). The application constructs file paths during ZIP extraction using `filepath.Join(destDir, f.Name)` without validating or sanitizing `f.Name`. If the ZIP archive contains entries with `../`, the resulting path can escape the intended directory, allowing writes to arbitrary locations on the host filesystem.

### Attack Requirements
There are several requirements needed to make this attack possible:
- The Traefik server should be deployed with [plugins enabled](https://doc.traefik.io/traefik/plugins/) with a WASM plugin (yaegi plugins are not impacted).
- The attacker should have write access to a remote plugin asset loaded by the Traefik server
- The attacker should craft a malicious version of this plugin

### Warning
As clearly stated in the [documentation](https://doc.traefik.io/traefik/plugins/), plugins are experimental in Traefik, and unsafe plugins could damage your infrastructure:

> **Experimental Features**
Plugins can change the behavior of Traefik in unforeseen ways. Exercise caution when adding new plugins to production Traefik instances.

### Impact
**This vulnerability did not affect any plugin from the catalog. There is no known impact. 
Additionally, the catalog will also prevent any compromised plugin to be available across all Traefik versions.**
This vulnerability can allow an attacker to perform arbitrary file write outside the intended plugin extraction directory by crafting a malicious ZIP archive that includes `../` (directory traversal) in file paths.

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-q6gg-9f92-r9wg
- https://nvd.nist.gov/vuln/detail/CVE-2025-54386
- https://github.com/traefik/plugin-service/pull/71
- https://github.com/traefik/plugin-service/pull/72
- https://github.com/traefik/traefik/pull/11911
- https://github.com/traefik/traefik/commit/5ef853a0c53068f69a6c229a5815a0dc6e0a8800
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.28
