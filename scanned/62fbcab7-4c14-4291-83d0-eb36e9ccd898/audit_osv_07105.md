# [H] Apache NiFi: Incorrect Authorization for Parameter Context Validation Requests

## Summary
Severity: High
Advisory: BIT-nifi-2026-62354
Aliases: CVE-2026-62354
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-nifi-2026-62354
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.10.0 <2.11.0

## Details
Authorization handling for Parameter Context validation requests in Apache NiFi 1.10.0 through 2.10.0 allows clients with read access to submit proposed Parameter values. The proposed values override current configuration, enabling users with read access to invoke predefined component validation methods with alternative settings. Apache NiFi installations that do not implement different levels of authorization for viewing and modifying Parameter Context configuration are not subject to this vulnerability. Upgrading to Apache NiFi 2.11.0 is the recommended mitigation, requiring write access to submit Parameter Context validation requests.

## References
- http://www.openwall.com/lists/oss-security/2026/08/03/11
- https://lists.apache.org/thread/l17xcnnf1rm7qljmypyjxmh62cx4o4wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-62354
