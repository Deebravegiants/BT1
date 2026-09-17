# [M] BIT-pinniped-2022-22975

## Summary
Severity: Medium
Advisory: BIT-pinniped-2022-22975
Aliases: CVE-2022-22975, GHSA-hvrf-5hhv-4348
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pinniped-2022-22975
Type: osv

## Affected
- Bitnami: `pinniped` — affected >=0.9.0 <0.17.0

## Details
An issue was discovered in the Pinniped Supervisor with either LADPIdentityProvider or ActiveDirectoryIdentityProvider resources. An attack would involve the malicious user changing the common name (CN) of their user entry on the LDAP or AD server to include special characters, which could be used to perform LDAP query injection on the Supervisor's LDAP query which determines their Kubernetes group membership.

## References
- https://github.com/vmware-tanzu/pinniped/security/advisories/GHSA-hvrf-5hhv-4348
- https://nvd.nist.gov/vuln/detail/CVE-2022-22975
