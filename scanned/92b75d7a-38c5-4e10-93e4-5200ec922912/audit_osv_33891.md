# [H] Apache Mynewt NimBLE: Invalid error handling in pause encryption procedure in NimBLE controller

## Summary
Severity: High
Advisory: CVE-2025-52435
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2025-52435
Type: osv

## Details
J2EE Misconfiguration: Data Transmission Without Encryption vulnerability in Apache NimBLE.

Improper handling of Pause Encryption procedure on Link Layer results in a previously encrypted connection being left in un-encrypted state allowing an eavesdropper to observe the remainder of the exchange.
This issue affects Apache NimBLE: through <= 1.8.0.

Users are recommended to upgrade to version 1.9.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/01/08/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52435.json
- https://lists.apache.org/thread/ow8dzpsqfh9llfclh5fzh6z237brzc0s
- https://nvd.nist.gov/vuln/detail/CVE-2025-52435
- https://github.com/apache/mynewt-nimble/commit/164f1c23c18a290908df76ed83fe848bfe4a4903
- https://github.com/apache/mynewt-nimble/commit/ec3d75e909fa6dcadf1836fefc4432794a673d18
