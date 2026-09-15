# [H] Apache NiFi: Improper Escaping of Table Names in CaptureChangeMySQL

## Summary
Severity: High
Advisory: BIT-nifi-2026-44913
Aliases: CVE-2026-44913
Ecosystem: Bitnami
Published: 2026-06-24
Source: https://osv.dev/vulnerability/BIT-nifi-2026-44913
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.2.0 <2.10.0

## Details
Improper escaping of database table names in the CaptureChangeMySQL Processor included with Apache NiFi 1.2.0 through 2.9.0 allows for injecting SQL commands using crafted naming. Manual quoted boundaries added in Apache NiFi 1.8.0 narrowed the scope of potential injection options, but did not cover additional strategies. Apache NiFi installations that do not use the CaptureChangeMySQL Processor are not subject to this vulnerability. Upgrading to Apache NiFi 2.10.0 is the recommended mitigation, which incorporates more robust identifier escaping.

## References
- http://www.openwall.com/lists/oss-security/2026/06/20/5
- https://lists.apache.org/thread/c8vkt5rz4dqql6sjxgrr3zdkbt1sfmsl
- https://nvd.nist.gov/vuln/detail/CVE-2026-44913
