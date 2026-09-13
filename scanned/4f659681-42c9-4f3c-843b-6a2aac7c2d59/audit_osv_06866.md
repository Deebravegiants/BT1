# [H] MongoDB Server may have unexpected application behaviour due to invalid BSON

## Summary
Severity: High
Advisory: BIT-mongodb-2024-3372
Aliases: CVE-2024-3372
Ecosystem: Bitnami
Published: 2025-09-23
Source: https://osv.dev/vulnerability/BIT-mongodb-2024-3372
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=7.0.0 <7.0.6

## Details
Improper validation of certain metadata input may result in the server not correctly serialising BSON. This can be performed pre-authentication and may cause unexpected application behavior including unavailability of serverStatus responses. This issue affects MongoDB Server v7.0 versions prior to 7.0.6, MongoDB Server v6.0 versions prior to 6.0.14 and MongoDB Server v.5.0 versions prior to 5.0.25.

## References
- https://jira.mongodb.org/browse/SERVER-85263
- https://nvd.nist.gov/vuln/detail/CVE-2024-3372
