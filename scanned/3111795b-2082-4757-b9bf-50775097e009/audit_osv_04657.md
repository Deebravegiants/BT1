# [C] BIT-ejbca-2022-34831

## Summary
Severity: Critical
Advisory: BIT-ejbca-2022-34831
Aliases: CVE-2022-34831
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-ejbca-2022-34831
Type: osv

## Affected
- Bitnami: `ejbca` — affected >=0 <7.9.0

## Details
An issue was discovered in Keyfactor PrimeKey EJBCA before 7.9.0, related to possible inconsistencies in DNS identifiers submitted in an ACME order and the corresponding CSR submitted during finalization. During the ACME enrollment process, an order is submitted containing an identifier for one or multiple dnsNames. These are validated properly in the ACME challenge. However, if the validation passes, a non-compliant client can include additional dnsNames the CSR sent to the finalize endpoint, resulting in EJBCA issuing a certificate including the identifiers that were not validated. This occurs even if the certificate profile is configured to not allow a DN override by the CSR.

## References
- https://support.keyfactor.com/s/detail/a6x1Q000000CwC5QAK
- https://www.primekey.com/products/ejbca-enterprise/
- https://nvd.nist.gov/vuln/detail/CVE-2022-34831
