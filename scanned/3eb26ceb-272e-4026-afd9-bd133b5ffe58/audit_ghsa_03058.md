# [H] Improper Certificate Validation in HashiCorp Nomad

## Summary
Severity: High
Advisory: GHSA-cj2h-ww36-v932
CVE: CVE-2020-7956
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-cj2h-ww36-v932
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <0.10.3

## Details
HashiCorp Nomad and Nomad Enterprise up to 0.10.2 incorrectly validated role/region associated with TLS certificates used for mTLS RPC, and were susceptible to privilege escalation. Fixed in 0.10.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7956
- https://github.com/hashicorp/nomad/issues/7003
- https://github.com/hashicorp/nomad/pull/7023
- https://www.hashicorp.com/blog/category/nomad
