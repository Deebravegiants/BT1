# [H] Firebird: Information leak vulnerability in firebird3 client when used with newer server

## Summary
Severity: High
Advisory: CVE-2025-65104
Aliases: GHSA-mfpr-9886-xjhg
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2025-65104
Type: osv

## Details
Firebird is an open-source relational database management system. In versions FB3 of the client library placed incorrect data length values into XSQLDA fields when communicating with FB4 or higher servers, resulting in an information leak. This issue is fixed by upgrading to the FB4 client or higher.

## References
- https://github.com/FirebirdSQL/firebird/releases/tag/v4.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65104.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-mfpr-9886-xjhg
- https://nvd.nist.gov/vuln/detail/CVE-2025-65104
