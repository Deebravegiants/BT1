# [C] Grafana plugin SDK Information Leakage

## Summary
Severity: Critical
Advisory: GHSA-xxxw-3j6h-q7h6
CVE: CVE-2024-8986
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-xxxw-3j6h-q7h6
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana-plugin-sdk-go` — affected >=0 <0.250.0

## Details
The grafana plugin SDK bundles build metadata into the binaries it compiles; this metadata includes the repository URI for the plugin being built, as retrieved by running `git remote get-url origin`.
 
If credentials are included in the repository URI (for instance, to allow for fetching of private dependencies), the final binary will contain the full URI, including said credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8986
- https://github.com/grafana/grafana-plugin-sdk-go/commit/aaa26d1bebaaf6160c37d3f1226a750eab70ca41
- https://github.com/grafana/grafana-plugin-sdk-go
- https://grafana.com/security/security-advisories/cve-2024-8986
- https://pkg.go.dev/vuln/GO-2024-3140
