# [H] Improper Authentication in HashiCorp Nomad

## Summary
Severity: High
Advisory: GHSA-2jhh-5xm2-j4gf
CVE: CVE-2021-43415
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-2jhh-5xm2-j4gf
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <1.0.14
- Go: `github.com/hashicorp/nomad` — affected >=1.1.0 <1.1.8
- Go: `github.com/hashicorp/nomad` — affected >=1.2.0 <1.2.1

## Details
HashiCorp Nomad and Nomad Enterprise up to 1.0.13, 1.1.7, and 1.2.0, with the QEMU task driver enabled, allowed authenticated users with job submission capabilities to bypass the configured allowed image paths. Fixed in 1.0.14, 1.1.8, and 1.2.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43415
- https://discuss.hashicorp.com/t/hcsec-2021-31-nomad-qemu-task-driver-allowed-paths-bypass-with-job-args/32288
- https://github.com/hashicorp/nomad
- https://www.hashicorp.com/blog/category/nomad
