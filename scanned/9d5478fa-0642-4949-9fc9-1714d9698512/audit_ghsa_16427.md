# [H] Helm's Missing YAML Content Leads To Panic

## Summary
Severity: High
Advisory: GHSA-r53h-jv2g-vpx6
CVE: CVE-2024-26147
CWE: CWE-457, CWE-908
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-r53h-jv2g-vpx6
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.14.2

## Details
A Helm contributor discovered uninitialized variable vulnerability when Helm parses index and plugin yaml files missing expected content.

### Impact

When either an `index.yaml` file or a plugins `plugin.yaml` file were missing all metadata a panic would occur in Helm.

In the Helm SDK this is found when using the `LoadIndexFile` or `DownloadIndexFile` functions in the `repo` package or the `LoadDir` function in the `plugin` package. For the Helm client this impacts functions around adding a repository and all Helm functions if a malicious plugin is added as Helm inspects all known plugins on each invocation.

### Patches

This issue has been resolved in Helm v3.14.2.

### Workarounds

If a malicious plugin has been added which is causing all Helm client commands to panic, the malicious plugin can be manually removed from the filesystem.

If using Helm SDK versions prior to 3.14.2, calls to affected functions can use `recover` to catch the panic.

### For more information

Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits

Disclosed by Jakub Ciolek at AlphaSense.

## References
- https://github.com/helm/helm/security/advisories/GHSA-r53h-jv2g-vpx6
- https://nvd.nist.gov/vuln/detail/CVE-2024-26147
- https://github.com/helm/helm/commit/bb4cc9125503a923afb7988f3eb478722a8580af
- https://github.com/helm/helm
