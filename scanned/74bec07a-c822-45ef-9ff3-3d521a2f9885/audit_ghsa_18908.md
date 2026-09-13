# [H] Apache Syncope's AES encryption stores hard-coded passwords in internal database

## Summary
Severity: High
Advisory: GHSA-jqg8-m35q-jh7j
CVE: CVE-2025-65998
CWE: CWE-321
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-jqg8-m35q-jh7j
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope-core` — affected >=4.0.0 <4.0.3
- Maven: `org.apache.syncope:syncope-core` — affected >=0 <3.0.15

## Details
Apache Syncope can be configured to store the user password values in the internal database with AES encryption, though this is not the default option.

When AES is configured, the default key value, hard-coded in the source code, is always used. This allows a malicious attacker, once obtained access to the internal database content, to reconstruct the original cleartext password values.
This is not affecting encrypted plain attributes, whose values are also stored using AES encryption.

Users are recommended to upgrade to version 3.0.15 / 4.0.3, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65998
- https://github.com/apache/syncope/commit/297498ebfc86e4996f5e3e4ef7b7f8b1cd82004b
- https://github.com/apache/syncope/commit/9d706af25d2e60327b8b5b63186f9da51ed79a1d
- https://github.com/apache/syncope
- https://lists.apache.org/thread/fjh0tb0d1xkbphc5ogdsc348ppz88cts
- http://www.openwall.com/lists/oss-security/2025/11/24/1
