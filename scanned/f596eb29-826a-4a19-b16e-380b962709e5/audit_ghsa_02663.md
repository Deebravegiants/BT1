# [M] HashiCorp Consul and Consul Enterprise 1.10.1 Txn.Apply endpoint allowed services to register proxies for other services, enabling access to service traffic.

## Summary
Severity: Medium
Advisory: GHSA-6hw5-6gcx-phmw
CVE: CVE-2021-38698
CWE: CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-6hw5-6gcx-phmw
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.10.1 <1.10.2
- Go: `github.com/hashicorp/consul` — affected >=1.9.0 <1.9.9
- Go: `github.com/hashicorp/consul` — affected >=0 <1.8.15

## Details
HashiCorp Consul and Consul Enterprise 1.10.1 Txn.Apply endpoint allowed services to register proxies for other services, enabling access to service traffic. Fixed in 1.8.15, 1.9.9 and 1.10.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38698
- https://github.com/hashicorp/consul/pull/10824
- https://discuss.hashicorp.com/t/hcsec-2021-24-consul-missing-authorization-check-on-txn-apply-endpoint/29026
- https://github.com/hashicorp/consul
- https://security.gentoo.org/glsa/202208-09
- https://www.hashicorp.com/blog/category/consul
