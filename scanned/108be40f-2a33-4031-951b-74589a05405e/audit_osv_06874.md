# [H] MongoDB C Driver bson library may be susceptible to buffer overflow

## Summary
Severity: High
Advisory: BIT-mongodb-2025-0755
Aliases: CVE-2025-0755
Ecosystem: Bitnami
Published: 2025-09-23
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-0755
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.1

## Details
The various bson_append functions in the MongoDB C driver library may be susceptible to buffer overflow when performing operations that could result in a final BSON document which exceeds the maximum allowable size (INT32_MAX), resulting in a segmentation fault and possible application crash. This issue affected libbson versions prior to 1.27.5, MongoDB Server v8.0 versions prior to 8.0.1 and MongoDB Server v7.0 versions prior to 7.0.16

## References
- https://jira.mongodb.org/browse/CDRIVER-5601
- https://jira.mongodb.org/browse/SERVER-94461
- https://nvd.nist.gov/vuln/detail/CVE-2025-0755
- https://lists.debian.org/debian-lts-announce/2025/05/msg00012.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00027.html
