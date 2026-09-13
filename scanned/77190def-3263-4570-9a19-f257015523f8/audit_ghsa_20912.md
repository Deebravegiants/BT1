# [H] HashiCorp Consul does not properly validate node or segment names prior to usage in JWT claim assertions

## Summary
Severity: High
Advisory: GHSA-hr3v-8cp3-68rf
CVE: CVE-2021-41803
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-hr3v-8cp3-68rf
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.8.1 <1.11.9
- Go: `github.com/hashicorp/consul` — affected >=1.12.0 <1.12.5
- Go: `github.com/hashicorp/consul` — affected >=1.13.0 <1.13.2

## Details
HashiCorp Consul 1.8.1 up to 1.11.8, 1.12.4, and 1.13.1 did not properly validate the node or segment names prior to interpolation and usage in JWT claim assertions with the auto config RPC. Fixed in 1.11.9, 1.12.5, and 1.13.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41803
- https://github.com/hashicorp/consul/pull/14577/commits/2c881259ce10e308ff03afc968c4165998fd7fee
- https://discuss.hashicorp.com/t/hcsec-2022-19-consul-auto-config-jwt-authorization-missing-input-validation/44627
- https://github.com/hashicorp/consul
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYZOKMMVX4SIEHPJW3SJUQGMO5YZCPHC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XNF4OLYZRQE75EB5TW5N42FSXHBXGWFE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZTE4ITXXPIWZEQ4HYQCB6N6GZIMWXDAI
