# [H] Privilege escalation in Hashicorp Nomad

## Summary
Severity: High
Advisory: GHSA-c8x3-rg72-fwwg
CVE: CVE-2021-37218
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-c8x3-rg72-fwwg
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <1.0.10
- Go: `github.com/hashicorp/nomad` — affected >=1.1.0 <1.1.4

## Details
HashiCorp Nomad and Nomad Enterprise Raft RPC layer allows non-server agents with a valid certificate signed by the same CA to access server-only functionality, enabling privilege escalation. Fixed in 1.0.10 and 1.1.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37218
- https://discuss.hashicorp.com/t/hcsec-2021-21-nomad-raft-rpc-privilege-escalation/29023
- https://github.com/hashicorp/nomad
- https://www.hashicorp.com/blog/category/nomad
