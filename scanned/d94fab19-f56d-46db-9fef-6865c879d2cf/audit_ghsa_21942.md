# [M] HashiCorp Nomad Artifact Download Race Condition

## Summary
Severity: Medium
Advisory: GHSA-gwmc-6795-qghj
CVE: CVE-2022-24686
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-gwmc-6795-qghj
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0.3.0 <1.0.18
- Go: `github.com/hashicorp/nomad` — affected >=1.1.0 <1.1.12
- Go: `github.com/hashicorp/nomad` — affected >=1.2.0 <1.2.6

## Details
HashiCorp Nomad and Nomad Enterprise 0.3.0 through 1.0.17, 1.1.11, and 1.2.5 artifact download functionality has a race condition such that the Nomad client agent could download the wrong artifact into the wrong destination. This issue is fixed in 1.0.18, 1.1.12, and 1.2.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24686
- https://github.com/hashicorp/nomad/issues/12036
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-01-nomad-artifact-download-race-condition/35559
- https://github.com/hashicorp/nomad
- https://github.com/hashicorp/nomad/releases/tag/v1.2.6
- https://security.netapp.com/advisory/ntap-20220318-0008
