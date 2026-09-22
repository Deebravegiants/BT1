# [H] JLSEC-2026-773

## Summary
Severity: High
Advisory: JLSEC-2026-773
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/JLSEC-2026-773
Type: osv

## Affected
- Julia: `MongoC_jll` — affected >=0 <1.30.8+0

## Details
The `bson_validate` function may return early on specific inputs and incorrectly report success. This behavior could result in skipping validation for BSON data, allowing malformed or invalid UTF-8 sequences to bypass validation and be processed incorrectly. The issue may affect applications that rely on these functions to validate untrusted BSON data before further processing. This issue affects MongoDB C Driver versions prior to 1.30.5, MongoDB C Driver version 2.0.0 and MongoDB C Driver version 2.0.1

## References
- https://jira.mongodb.org/browse/CDRIVER-6017
