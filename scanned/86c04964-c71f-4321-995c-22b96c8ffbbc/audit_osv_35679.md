# [H] CVE-2026-12609

## Summary
Severity: High
Advisory: CVE-2026-12609
Aliases: GHSA-qmm6-p8q4-2g48
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-12609
Type: osv

## Details
In Eclipse Theia versions 1.66.0 and up until including 1.73.1, the `@theia/plugin-ext` backend exposes the `/hostedPlugin/:pluginId/:path(*)` HTTP endpoint, which resolves the requested file path with `path.resolve(localPath, filePath)` without verifying that the resolved path stays within the plugin's directory. An unauthenticated network attacker can send percent-encoded `../` sequences (`%2e%2e%2f`) that decode into the path parameter and escape the plugin directory, allowing arbitrary files readable by the Theia backend process to be retrieved. Plugin IDs are derived deterministically from a plugin's publisher and name, so built-in plugins serve as reliable anchors that require no prior knowledge of the target system.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12609.json
- https://github.com/eclipse-theia/theia/security/advisories/GHSA-qmm6-p8q4-2g48
- https://nvd.nist.gov/vuln/detail/CVE-2026-12609
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/524
