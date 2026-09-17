# [M] Nomad ACL Policies without Label are Applied to Unexpected Resources

## Summary
Severity: Medium
Advisory: GHSA-rpvr-38xv-xvxq
CVE: CVE-2023-3072
CWE: CWE-266, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-rpvr-38xv-xvxq
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/nomad` — affected >=0.7.0 <1.4.11
- Go: `github.com/hashicorp/nomad` — affected >=1.5.0 <1.5.6

## Details
A vulnerability was identified in Nomad, an ACL policy using a block without label may be applied to unexpected resources. This vulnerability, CVE-2023-3072, affects Nomad from 0.7 up to 1.5.6 and 1.4.10 and was fixed in 1.6.0, 1.5.7, and 1.4.11.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3072
- https://discuss.hashicorp.com/t/hcsec-2023-20-nomad-acl-policies-without-label-are-applied-to-unexpected-resources/56270
- https://github.com/hashicorp/nomad
- https://pkg.go.dev/vuln/GO-2024-2670
