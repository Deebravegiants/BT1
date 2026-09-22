# [M] Uncaught Exception in Kibana Cases Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elk-2026-49096
Aliases: BIT-kibana-2026-49096, CVE-2026-49096
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-49096
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.2

## Details
Uncaught Exception (CWE-248) in Kibana Cases can lead to denial of service via Input Data Manipulation (CAPEC-153). Malformed link syntax stored in a case comment was not rejected or sanitized when the comment was later formatted for display, and the resulting unhandled error prevented the affected case from being displayed. An authenticated user holding privileges to comment on a case could store such a comment, after which that case became inaccessible to every user who opened it until the stored comment was removed.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-9-3-5-9-4-2-security-update-esa-2026-136/389492
- https://nvd.nist.gov/vuln/detail/CVE-2026-49096
