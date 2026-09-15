# [H] Arbitrary file reads in HashiCorp Nomad

## Summary
Severity: High
Advisory: GHSA-wmrx-57hm-mw7r
CVE: CVE-2022-24683
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-18
Source: https://github.com/advisories/GHSA-wmrx-57hm-mw7r
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0.9.2 <1.0.18
- Go: `github.com/hashicorp/nomad` — affected >=1.1.0 <1.1.12
- Go: `github.com/hashicorp/nomad` — affected >=1.2.0 <1.2.6

## Details
Nomad is an easy-to-use, flexible, and performant workload orchestrator that can deploy a mix of microservice, batch, containerized, and non-containerized applications. HashiCorp Nomad and Nomad Enterprise 0.9.2 through 1.0.17, 1.1.11, and 1.2.5 allow operators with read-fs and alloc-exec (or job-submit) capabilities to read arbitrary files on the host filesystem as root. There are currently no known workarounds. Users are recommended to upgrade as soon as possible to avoid this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24683
- https://github.com/hashicorp/nomad/commit/1aa46c3796e924b72eb45a7f02dae32df0c1179c
- https://github.com/hashicorp/nomad/commit/b3c0e6a7a53d624003698b48b6c59739552c3721
- https://github.com/hashicorp/nomad/commit/fcb3a5d016a3dfcc63efcdb567373735a0703279
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-02-nomad-alloc-filesystem-and-container-escape/35560
- https://security.netapp.com/advisory/ntap-20220318-0008
- github.com/hashicorp/nomad
