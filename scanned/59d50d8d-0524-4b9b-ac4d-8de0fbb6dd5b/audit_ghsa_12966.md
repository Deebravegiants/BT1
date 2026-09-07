# [H] Consul JWT Auth in L7 Intentions Allow for Mismatched Service Identity and JWT Providers

## Summary
Severity: High
Advisory: GHSA-9rhf-q362-77mx
CVE: CVE-2023-3518
CWE: CWE-266, CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-9rhf-q362-77mx
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.16.0 <1.16.1

## Details
A vulnerability was identified in Consul such that using JWT authentication for service mesh incorrectly allows/denies access regardless of service identities. This vulnerability, CVE-2023-3518, affects Consul 1.16.0 and was fixed in 1.16.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3518
- https://discuss.hashicorp.com/t/hcsec-2023-25-consul-jwt-auth-in-l7-intentions-allow-for-mismatched-service-identity-and-jwt-providers/57004
- https://github.com/hashicorp/consul
