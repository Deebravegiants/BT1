# [H] BIT-ejbca-2020-25276

## Summary
Severity: High
Advisory: BIT-ejbca-2020-25276
Aliases: CVE-2020-25276
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ejbca-2020-25276
Type: osv

## Affected
- Bitnami: `ejbca` — affected >=7.0.0 <7.4.1

## Details
An issue was discovered in PrimeKey EJBCA 6.x and 7.x before 7.4.1. When using a client certificate to enroll over the EST protocol, no revocation check is performed on that certificate. This vulnerability can only affect a system that has EST configured, uses client certificates to authenticate enrollment, and has had such a certificate revoked. This certificate needs to belong to a role that is authorized to enroll new end entities. (To completely mitigate this problem prior to upgrade, remove any revoked client certificates from their respective roles.)

## References
- https://support.primekey.com/news/posts/ejbca-security-advisory-revocation-check-not-performed-on-est-client-certificate
- https://nvd.nist.gov/vuln/detail/CVE-2020-25276
