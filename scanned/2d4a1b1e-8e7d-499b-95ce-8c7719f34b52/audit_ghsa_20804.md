# [M] HashiCorp Consul vulnerable to authorization bypass

## Summary
Severity: Medium
Advisory: GHSA-m69r-9g56-7mv8
CVE: CVE-2022-40716
CWE: CWE-252
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-m69r-9g56-7mv8
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.11.9
- Go: `github.com/hashicorp/consul` — affected >=1.12.0 <1.12.5
- Go: `github.com/hashicorp/consul` — affected >=1.13.0 <1.13.2

## Details
HashiCorp Consul and Consul Enterprise versions prior to 1.11.9, 1.12.5, and 1.13.2 do not check for multiple SAN URI values in a CSR on the internal RPC endpoint, enabling leverage of privileged access to bypass service mesh intentions. A specially crafted CSR sent directly to Consul’s internal server agent RPC endpoint can include multiple SAN URI values with additional service names. This issue has been fixed in versions 1.11.9, 1.12.5, and 1.13.2. There are no known workarounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40716
- https://github.com/hashicorp/consul/pull/14579
- https://github.com/hashicorp/consul/commit/8f6fb4f6fe9488b8ec37da71ac503081d7d3760b
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-20-consul-service-mesh-intention-bypass-with-malicious-certificate-signing-request/44628
- https://github.com/hashicorp/consul
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYZOKMMVX4SIEHPJW3SJUQGMO5YZCPHC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZTE4ITXXPIWZEQ4HYQCB6N6GZIMWXDAI
