# [H] CVE-2018-19786

## Summary
Severity: High
Advisory: CVE-2018-19786
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-05
Source: https://osv.dev/vulnerability/CVE-2018-19786
Type: osv

## Details
HashiCorp Vault before 1.0.0 writes the master key to the server log in certain unusual or misconfigured scenarios in which incorrect data comes from the autoseal mechanism without an error being reported.

## References
- https://github.com/hashicorp/vault/blob/master/CHANGELOG.md#100-december-3rd-2018
