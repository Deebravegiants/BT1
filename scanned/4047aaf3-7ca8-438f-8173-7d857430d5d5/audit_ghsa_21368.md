# [M] Nomad Panics On Job Submission With Bad Artifact Stanza Source URL

## Summary
Severity: Medium
Advisory: GHSA-7v3g-4878-5qrf
CVE: CVE-2022-41606
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-7v3g-4878-5qrf
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0 <1.2.13
- Go: `github.com/hashicorp/nomad` — affected >=1.3.0 <1.3.6

## Details
HashiCorp Nomad and Nomad Enterprise 1.0.2 up to 1.2.12, and 1.3.5 jobs submitted with an artifact stanza using invalid S3 or GCS URLs can be used to crash client agents. Fixed in 1.2.13, 1.3.6, and 1.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41606
- https://discuss.hashicorp.com
- https://discuss.hashicorp.com/t/hcsec-2022-22-nomad-panics-on-job-submission-with-bad-artifact-stanza-source-url/45420
- https://github.com/hashicorp/nomad
- https://pkg.go.dev/vuln/GO-2022-1062
