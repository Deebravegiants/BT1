# [M] BIT-nifi-2020-13940

## Summary
Severity: Medium
Advisory: BIT-nifi-2020-13940
Aliases: CVE-2020-13940, GHSA-q4xf-3pmq-3hw8
Ecosystem: Bitnami
Published: 2025-09-12
Source: https://osv.dev/vulnerability/BIT-nifi-2020-13940
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.0.0

## Details
In Apache NiFi 1.0.0 to 1.11.4, the notification service manager and various policy authorizer and user group provider objects allowed trusted administrators to inadvertently configure a potentially malicious XML file. The XML file has the ability to make external calls to services (via XXE).

## References
- https://nifi.apache.org/security#CVE-2020-13940
- https://nvd.nist.gov/vuln/detail/CVE-2020-13940
