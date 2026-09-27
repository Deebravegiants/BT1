# [H] Helm vulnerable to Code Injection through malicious chart.yaml content

## Summary
Severity: High
Advisory: GHSA-557j-xg8c-q2mm
CVE: CVE-2025-53547
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2025-07-08
Source: https://github.com/advisories/GHSA-557j-xg8c-q2mm
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=3.18.0-rc.1 <3.18.4
- Go: `helm.sh/helm/v3` — affected >=0 <3.17.4

## Details
A Helm contributor discovered that a specially crafted `Chart.yaml` file along with a specially linked `Chart.lock` file can lead to local code execution when dependencies are updated.

### Impact

Fields in a `Chart.yaml` file, that are carried over to a `Chart.lock` file when dependencies are updated and this file is written, can be crafted in a way that can cause execution if that same content were in a file that is executed (e.g., a `bash.rc` file or shell script). If the `Chart.lock` file is symlinked to one of these files updating dependencies will write the lock file content to the symlinked file. This can lead to unwanted execution. Helm warns of the symlinked file but did not stop execution due to symlinking.

This affects when dependencies are updated. When using the `helm` command this happens when `helm dependency update` is run. `helm dependency build` can write a lock file when one does not exist but this vector requires one to already exist. This affects the Helm SDK when the downloader `Manager` performs an update.

### Patches

This issue has been resolved in Helm v3.18.4

### Workarounds

Ensure the `Chart.lock` file in a chart is not a symlink prior to updating dependencies.

### For more information

Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits

Disclosed by Jakub Ciolek at AlphaSense.

## References
- https://github.com/helm/helm/security/advisories/GHSA-557j-xg8c-q2mm
- https://nvd.nist.gov/vuln/detail/CVE-2025-53547
- https://github.com/helm/helm/commit/4b8e61093d8f579f1165cdc6bd4b43fa5455f571
- https://github.com/helm/helm
- https://news.ycombinator.com/item?id=44506696
