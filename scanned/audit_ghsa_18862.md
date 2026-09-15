# [M] Consul event endpoint is vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-qh7p-pfq3-677h
CVE: CVE-2025-11375
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-qh7p-pfq3-677h
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.22.0

## Details
Consul and Consul Enterprise’s (“Consul”) event endpoint is vulnerable to denial of service (DoS) due to lack of maximum value on the Content Length header. This vulnerability, CVE-2025-11375, is fixed in Consul Community Edition 1.22.0 and Consul Enterprise 1.22.0, 1.21.6, 1.20.8 and 1.18.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11375
- https://github.com/hashicorp/consul/pull/22836
- https://github.com/hashicorp/consul/commit/e794201d0c618333d81ad775270f7b32801178fb
- https://discuss.hashicorp.com/t/hcsec-2025-28-consuls-event-endpoint-is-vulnerable-to-denial-of-service/76723
- https://github.com/hashicorp/consul
- https://github.com/hashicorp/consul/releases/tag/v1.22.0
- https://pkg.go.dev/vuln/GO-2025-4082
