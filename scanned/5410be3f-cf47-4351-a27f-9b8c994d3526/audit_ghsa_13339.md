# [M] Nomad Search API Leaks Information About CSI Plugins

## Summary
Severity: Medium
Advisory: GHSA-v5fm-hr72-27hx
CVE: CVE-2023-3300
CWE: CWE-266, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-v5fm-hr72-27hx
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0.11.0 <1.4.11
- Go: `github.com/hashicorp/nomad` — affected >=1.5.0 <1.5.7

## Details
A vulnerability was identified in Nomad such that the search HTTP API can reveal names of available CSI plugins to unauthenticated users or users without the plugin:read policy. This vulnerability, CVE-2023-3300, affects Nomad since 0.11 and was fixed in 1.6.0, 1.5.7, and 1.4.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3300
- https://github.com/hashicorp/nomad/commit/a8789d3872bbf1b1f420f28b0f7ad8532a41d5e3
- https://discuss.hashicorp.com/t/hcsec-2023-22-nomad-search-api-leaks-information-about-csi-plugins/56272
- https://github.com/hashicorp/nomad
- https://pkg.go.dev/vuln/GO-2024-2671
