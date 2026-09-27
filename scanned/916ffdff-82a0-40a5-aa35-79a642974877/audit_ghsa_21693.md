# [C] Use After Free in HashiCorp Nomad

## Summary
Severity: Critical
Advisory: GHSA-77cr-6gr8-7rr9
CVE: CVE-2020-27195
CWE: CWE-416
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-77cr-6gr8-7rr9
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0.9.0 <0.10.6
- Go: `github.com/hashicorp/nomad` — affected >=0.11.0 <0.11.5
- Go: `github.com/hashicorp/nomad` — affected >=0.12.0 <0.12.6

## Details
HashiCorp Nomad and Nomad Enterprise version 0.9.0 up to 0.12.5 client file sandbox feature can be subverted using either the template or artifact stanzas. Fixed in 0.12.6, 0.11.5, and 0.10.6

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27195
- https://github.com/hashicorp/nomad/issues/9129
- https://github.com/hashicorp/nomad/pull/9139
- https://github.com/hashicorp/nomad/blob/master/CHANGELOG.md#0126-october-21-2020
- https://pkg.go.dev/github.com/hashicorp/nomad/client/allocrunner/taskrunner/template
- https://www.nomadproject.io/downloads
