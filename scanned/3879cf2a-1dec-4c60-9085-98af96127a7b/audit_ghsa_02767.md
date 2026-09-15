# [H] HashiCorp Consul L7 deny intention results in an allow action

## Summary
Severity: High
Advisory: GHSA-8h2g-r292-j8xh
CVE: CVE-2021-36213
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-07-19
Source: https://github.com/advisories/GHSA-8h2g-r292-j8xh
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=0 <1.10.1

## Details
In HashiCorp Consul before 1.10.1 (and Consul Enterprise), xds can generate a situation where a single L7 deny intention (with a default deny policy) results in an allow action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36213
- https://discuss.hashicorp.com/t/hcsec-2021-16-consul-s-application-aware-intentions-deny-action-fails-open-when-combined-with-default-deny-policy/26855
- https://github.com/hashicorp/consul
- https://github.com/hashicorp/consul/releases/tag/v1.10.1
- https://security.gentoo.org/glsa/202208-09
- https://www.hashicorp.com/blog/category/consul
