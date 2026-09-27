# [M] Helm dependency management path traversal

## Summary
Severity: Medium
Advisory: GHSA-v53g-5gjp-272r
CVE: CVE-2024-25620
CWE: CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-15
Source: https://github.com/advisories/GHSA-v53g-5gjp-272r
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.14.1

## Details
A Helm contributor discovered a path traversal vulnerability when Helm saves a chart including at download time.

### Impact

When either the Helm client or SDK is used to save a chart whose name within the `Chart.yaml` file includes a relative path change, the chart would be saved outside its expected directory based on the changes in the relative path. The validation and linting did not detect the path changes in the name.

### Patches

This issue has been resolved in Helm v3.14.1.

### Workarounds

Check all charts used by Helm for path changes in their name as found in the `Chart.yaml` file. This includes dependencies.

### Credits

Disclosed by Dominykas Blyžė at Nearform Ltd.

## References
- https://github.com/helm/helm/security/advisories/GHSA-v53g-5gjp-272r
- https://nvd.nist.gov/vuln/detail/CVE-2024-25620
- https://github.com/helm/helm/commit/0d0f91d1ce277b2c8766cdc4c7aa04dbafbf2503
- https://github.com/helm/helm
- https://github.com/helm/helm/releases/tag/v3.14.1
