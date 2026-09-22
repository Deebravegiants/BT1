# [H] HashiCorp Boundary Workers Store Rotated Credentials in Plaintext Even When Key Management Service Configured

## Summary
Severity: High
Advisory: GHSA-9vrm-v9xv-x3xr
CVE: CVE-2023-0690
CWE: CWE-311, CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-9vrm-v9xv-x3xr
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/boundary` — affected >=0.10.0 <0.12.0

## Details
HashiCorp Boundary from 0.10.0 through 0.11.2 contain an issue where when using a PKI-based worker with a Key Management Service (KMS) defined in the configuration file, new credentials created after an automatic rotation may not have been encrypted via the intended KMS. This would result in the credentials being stored in plaintext on the Boundary PKI worker’s disk. This issue is fixed in version 0.12.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0690
- https://discuss.hashicorp.com/t/hcsec-2023-03-boundary-workers-store-rotated-credentials-in-plaintext-even-when-key-management-service-configured/49907
- https://github.com/hashicorp/boundary
