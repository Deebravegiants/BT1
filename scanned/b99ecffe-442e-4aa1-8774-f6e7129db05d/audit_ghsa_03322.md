# [H] Use of a Broken or Risky Cryptographic Algorithm in Terraform

## Summary
Severity: High
Advisory: GHSA-h3p9-wrgx-82cm
CVE: CVE-2019-19316
CWE: CWE-20, CWE-327
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-h3p9-wrgx-82cm
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/terraform` — affected >=0 <0.12.17

## Details
When using the Azure backend with a shared access signature (SAS), Terraform versions prior to 0.12.17 may transmit the token and state snapshot using cleartext HTTP.

### Specific Go Packages Affected
github.com/hashicorp/terraform/backend/remote-state/azure

## References
- https://github.com/hashicorp/terraform/security/advisories/GHSA-4rvg-555h-r626
- https://nvd.nist.gov/vuln/detail/CVE-2019-19316
- https://github.com/hashicorp/terraform/issues/23493
- https://github.com/hashicorp/terraform/commit/6db3cf8e5b4cfb2a3cd1d99a813b50b2d5d363bb
- https://github.com/hashicorp/terraform
- https://pkg.go.dev/vuln/GO-2022-0839
