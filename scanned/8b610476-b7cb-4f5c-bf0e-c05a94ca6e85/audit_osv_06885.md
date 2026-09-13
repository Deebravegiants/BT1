# [H] Zlib compressed protocol header length confusion may allow memory read

## Summary
Severity: High
Advisory: BIT-mongodb-2025-14847
Aliases: CVE-2025-14847
Ecosystem: Bitnami
Published: 2025-12-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-14847
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.3

## Details
Mismatched length fields in Zlib compressed protocol headers may allow a read of uninitialized heap memory by an unauthenticated client. This issue affects all MongoDB Server v7.0 prior to 7.0.28 versions, MongoDB Server v8.0 versions prior to 8.0.17, MongoDB Server v8.2 versions prior to 8.2.3, MongoDB Server v6.0 versions prior to 6.0.27, MongoDB Server v5.0 versions prior to 5.0.32, MongoDB Server v4.4 versions prior to 4.4.30, MongoDB Server v4.2 versions greater than or equal to 4.2.0, MongoDB Server v4.0 versions greater than or equal to 4.0.0, and MongoDB Server v3.6 versions greater than or equal to 3.6.0.

## References
- https://jira.mongodb.org/browse/SERVER-115508
- http://www.openwall.com/lists/oss-security/2025/12/29/21
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-14847
- https://nvd.nist.gov/vuln/detail/CVE-2025-7259
