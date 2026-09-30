# [M] Consul key/value endpoint is vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-7g3r-8c6v-hfmr
CVE: CVE-2025-11374
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-7g3r-8c6v-hfmr
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.22.0

## Details
Consul and Consul Enterprise’s (“Consul”) key/value endpoint is vulnerable to denial of service (DoS) due to incorrect Content Length header validation. This vulnerability, CVE-2025-11374, is fixed in Consul Community Edition 1.22.0 and Consul Enterprise 1.22.0, 1.21.6, 1.20.8 and 1.18.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11374
- https://github.com/hashicorp/consul/pull/22916
- https://github.com/hashicorp/consul/commit/72a358cd02533477536ad4bd2b781f520fa7fac6
- https://discuss.hashicorp.com/t/hcsec-2025-29-consuls-kv-endpoint-is-vulnerable-to-denial-of-service/76724
- https://github.com/hashicorp/consul
- https://github.com/hashicorp/consul/releases/tag/v1.22.0
- https://pkg.go.dev/vuln/GO-2025-4081
