# [C] CVE-2021-30476

## Summary
Severity: Critical
Advisory: CVE-2021-30476
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-22
Source: https://osv.dev/vulnerability/CVE-2021-30476
Type: osv

## Details
HashiCorp Terraform’s Vault Provider (terraform-provider-vault) did not correctly configure GCE-type bound labels for Vault’s GCP auth method. Fixed in 2.19.1.

## References
- https://discuss.hashicorp.com/t/hcsec-2021-11-terraform-s-vault-provider-did-not-correctly-configure-bound-labels-for-gcp-auth/23464/2
- https://github.com/hashicorp/terraform-provider-vault/issues/996
