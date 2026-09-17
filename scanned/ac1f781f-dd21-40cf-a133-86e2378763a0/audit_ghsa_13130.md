# [M] Terraform allows arbitrary file write during the `init` operation

## Summary
Severity: Medium
Advisory: GHSA-h626-pv66-hhm7
CVE: CVE-2023-4782
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2023-09-08
Source: https://github.com/advisories/GHSA-h626-pv66-hhm7
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/terraform` — affected >=1.0.8 <1.5.7

## Details
Terraform version 1.0.8 through 1.5.6 allows arbitrary file write during the `init` operation if run on maliciously crafted Terraform configuration. This vulnerability is fixed in Terraform 1.5.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4782
- https://github.com/hashicorp/terraform/pull/33745
- https://github.com/hashicorp/terraform/commit/0f2314fb62193c4be94328cc026fcb7ec1e9b893
- https://discuss.hashicorp.com/t/hcsec-2023-27-terraform-allows-arbitrary-file-write-during-init-operation/58082
- https://github.com/hashicorp/terraform
- https://github.com/hashicorp/terraform/releases/tag/v1.5.7
