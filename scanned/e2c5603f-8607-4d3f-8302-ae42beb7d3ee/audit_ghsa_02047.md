# [H] Improper Privilege Management in HashiCorp Nomad

## Summary
Severity: High
Advisory: GHSA-35qp-xq9f-2rjx
CVE: CVE-2021-3283
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-24
Source: https://github.com/advisories/GHSA-35qp-xq9f-2rjx
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=1.0.0 <1.0.3
- Go: `github.com/hashicorp/nomad` — affected >=0 <0.12.10

## Details
HashiCorp Nomad and Nomad Enterprise up to 0.12.9 exec and java task drivers can access processes associated with other tasks on the same node. Fixed in 0.12.10, and 1.0.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3283
- https://discuss.hashicorp.com/t/hcsec-2021-01-nomad-s-exec-and-java-task-drivers-did-not-isolate-processes/20332
