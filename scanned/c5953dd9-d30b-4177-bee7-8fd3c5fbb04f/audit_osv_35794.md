# [M] CVE-2026-14574

## Summary
Severity: Medium
Advisory: CVE-2026-14574
Aliases: GHSA-f3w9-qfw3-xr32
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:L/VI:H/VA:L/SC:N/SI:L/SA:L)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-14574
Type: osv

## Details
In Eclipse Theia versions 0.7.0 and up until including 1.73.1, the `PreferenceUtils.merge` function in `@theia/core` recursively merges preference values without rejecting prototype-related keys (`__proto__`, `constructor`, `prototype`). Because this function is invoked by `PreferenceServiceImpl.doResolve` for every preference resolution across scopes (default, user, workspace, folder), a crafted preference value in a workspace settings file (`.theia/settings.json` or `.vscode/settings.json`) can pollute `Object.prototype` when the user opens the workspace, potentially altering application logic across the Theia process.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/157
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14574.json
- https://github.com/eclipse-theia/theia/security/advisories/GHSA-f3w9-qfw3-xr32
- https://nvd.nist.gov/vuln/detail/CVE-2026-14574
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/567
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/567
