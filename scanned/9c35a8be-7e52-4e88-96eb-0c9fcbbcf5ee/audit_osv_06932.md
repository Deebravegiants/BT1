# [H] MD5 checksum creation may cause availability loss

## Summary
Severity: High
Advisory: BIT-mongodb-2026-6914
Aliases: CVE-2026-6914
Ecosystem: Bitnami
Published: 2026-05-08
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-6914
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.1.0 <8.2.7

## Details
Computing the MD5 checksum of a malformed BSON object under specific conditions may cause loss of availability in MongoDB server.
This issue affects all MongoDB Server v8.2 versions, all MongoDB Server v8.1 versions, MongoDB Server v8.0 versions prior to 8.0.21, MongoDB Server v7.0 versions prior to 7.0.32

## References
- https://jira.mongodb.org/browse/SERVER-119981
- https://nvd.nist.gov/vuln/detail/CVE-2026-6914
