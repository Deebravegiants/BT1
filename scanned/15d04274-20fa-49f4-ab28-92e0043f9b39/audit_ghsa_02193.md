# [H] Authentication Bypass by Spoofing and Insufficient Verification of Data Authenticity in Hashicorp Vault

## Summary
Severity: High
Advisory: GHSA-fp52-qw33-mfmw
CVE: CVE-2020-16250
CWE: CWE-290, CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-fp52-qw33-mfmw
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.8.1 <1.2.5
- Go: `github.com/hashicorp/vault` — affected >=1.3.0 <1.3.8
- Go: `github.com/hashicorp/vault` — affected >=1.4.0 <1.4.4
- Go: `github.com/hashicorp/vault` — affected >=1.5.0 <1.5.1

## Details
HashiCorp Vault and Vault Enterprise versions 0.7.1 and newer, when configured with the AWS IAM auth method, may be vulnerable to authentication bypass. Fixed in 1.2.5, 1.3.8, 1.4.4, and 1.5.1..

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-16250
- https://github.com/hashicorp/vault
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#151
- https://www.hashicorp.com/blog/category/vault
- http://packetstormsecurity.com/files/159478/Hashicorp-Vault-AWS-IAM-Integration-Authentication-Bypass.html
