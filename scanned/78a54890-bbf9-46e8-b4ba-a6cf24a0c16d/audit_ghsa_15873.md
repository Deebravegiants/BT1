# [M] Hashicorp Consul Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-99wr-c2px-grmh
CVE: CVE-2024-10086
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-99wr-c2px-grmh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.4.1 <1.20.0

## Details
A vulnerability was identified in Consul and Consul Enterprise such that the server response did not explicitly set a Content-Type HTTP header, allowing user-provided inputs to be misinterpreted and lead to reflected XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10086
- https://github.com/hashicorp/consul/commit/07fae7bb0be8593cc98c38b1ef4a49ed9188932f
- https://discuss.hashicorp.com/t/hcsec-2024-24-consul-vulnerable-to-reflected-xss-on-content-type-error-manipulation
- https://github.com/advisories/GHSA-99wr-c2px-grmh
- https://github.com/hashicorp/consul
- https://security.netapp.com/advisory/ntap-20250110-0006
