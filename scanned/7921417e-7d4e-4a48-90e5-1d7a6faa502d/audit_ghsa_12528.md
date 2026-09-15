# [H] HashiCorp Consul Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-h65h-v7fw-4p38
CVE: CVE-2019-12291
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-h65h-v7fw-4p38
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.4.0 <1.5.1

## Details
HashiCorp Consul 1.4.0 through 1.5.0 has Incorrect Access Control. Keys not matching a specific ACL rule used for prefix matching in a policy can be deleted by a token using that policy even with default deny settings configured.

### Specific Go Packages Affected
github.com/hashicorp/consul/acl

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12291
- https://github.com/hashicorp/consul/issues/5888
- https://github.com/hashicorp/consul/commit/36ebca1fd0129278487c6570449bc8cc03987890
- https://github.com/hashicorp/consul
- https://www.hashicorp.com/blog/category/consul
