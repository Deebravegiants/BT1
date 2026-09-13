# [M] BIT-ejbca-2021-40088

## Summary
Severity: Medium
Advisory: BIT-ejbca-2021-40088
Aliases: CVE-2021-40088
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ejbca-2021-40088
Type: osv

## Affected
- Bitnami: `ejbca` — affected >=0 <7.6.0

## Details
An issue was discovered in PrimeKey EJBCA before 7.6.0. CMP RA Mode can be configured to use a known client certificate to authenticate enrolling clients. The same RA client certificate is used for revocation requests as well. While enrollment enforces multi tenancy constraints (by verifying that the client certificate has access to the CA and Profiles being enrolled against), this check was not performed when authenticating revocation operations, allowing a known tenant to revoke a certificate belonging to another tenant.

## References
- https://support.primekey.com/news/posts/51
- https://nvd.nist.gov/vuln/detail/CVE-2021-40088
