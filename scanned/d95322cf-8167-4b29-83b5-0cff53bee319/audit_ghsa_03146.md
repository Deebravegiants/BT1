# [H] Allocation of Resources Without Limits or Throttling in HashiCorp Nomad

## Summary
Severity: High
Advisory: GHSA-h43v-26r7-7j4c
CVE: CVE-2020-7218
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-h43v-26r7-7j4c
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <0.10.3

## Details
HashiCorp Nomad and Nomad Enterprise before 0.10.3 allow unbounded resource usage.

### Specific Go Packages Affected
github.com/hashicorp/nomad/command/agent

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7218
- https://github.com/hashicorp/nomad/issues/7002
- https://github.com/hashicorp/nomad/pull/7022
- https://github.com/hashicorp/nomad
- https://www.hashicorp.com/blog/category/nomad
