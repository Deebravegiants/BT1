# [M] Malformed $group Query May Cause MongoDB Server to Crash

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-10061
Aliases: CVE-2025-10061
Ecosystem: Bitnami
Published: 2025-09-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-10061
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.1.0 <8.1.2

## Details
An authorized user can cause a crash in the MongoDB Server through a specially crafted $group query. This vulnerability is related to the incorrect handling of certain accumulator functions when additional parameters are specified within the $group operation. This vulnerability could lead to denial of service if triggered repeatedly. This issue affects MongoDB Server v6.0 versions prior to 6.0.25, MongoDB Server v7.0 versions prior to 7.0.22, MongoDB Server v8.0 versions prior to 8.0.12 and MongoDB Server v8.1 versions prior to 8.1.2

## References
- https://jira.mongodb.org/browse/SERVER-99616
- https://nvd.nist.gov/vuln/detail/CVE-2025-10061
