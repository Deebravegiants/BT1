# [H] Improper Input Validation in vault-ssh-helper

## Summary
Severity: High
Advisory: GHSA-f9fq-vjvh-779p
CVE: CVE-2020-24359
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-f9fq-vjvh-779p
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault-ssh-helper` — affected >=0 <0.2.0

## Details
HashiCorp vault-ssh-helper (github.com/hashicorp/vault-ssh-helper/helper) up to and including version 0.1.6 incorrectly accepted Vault-issued SSH OTPs for the subnet in which a host's network interface was located, rather than the specific IP address assigned to that interface. Fixed in 0.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24359
- https://github.com/hashicorp/vault-ssh-helper/commit/83effd08cbcbe4b993d776bd9b39465cd9e4603f
- https://github.com/hashicorp/vault-ssh-helper/blob/master/CHANGELOG.md#020-august-19-2020
- https://github.com/hashicorp/vault-ssh-helper/releases
