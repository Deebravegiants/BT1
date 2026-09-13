# [H] HashiCorp Consul Access Restriction Bypass

## Summary
Severity: High
Advisory: GHSA-fhm8-cxcv-pwvc
CVE: CVE-2019-8336
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fhm8-cxcv-pwvc
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/consul` — affected >=1.4.0 <1.4.3

## Details
HashiCorp Consul (and Consul Enterprise) 1.4.x before 1.4.3 allows a client to bypass intended access restrictions and obtain the privileges of one other arbitrary token within secondary datacenters, because a token with literally "<hidden>" as its secret is used in unusual circumstances.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-8336
- https://github.com/hashicorp/consul/issues/5423
- https://github.com/hashicorp/consul/commit/90040f8bffb311e6cd8599273e95b607175e311f
- https://github.com/hashicorp/consul
- https://github.com/hashicorp/consul/blob/003370ded024096cd89fb2aa2bc15293c23b9707/agent/consul/leader.go#L405
