# [H] Arbitrary File Read in Google BigQuery Sink connector

## Summary
Severity: High
Advisory: CVE-2026-23529
Aliases: GHSA-3mg8-2g53-5gj4
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/CVE-2026-23529
Type: osv

## Details
Kafka Connect BigQuery Connector is an implementation of a sink connector from Apache Kafka to Google BigQuery. Prior to 2.11.0, there is an arbitrary file read in Google BigQuery Sink connector. Aiven's Google BigQuery Kafka Connect Sink connector requires Google Cloud credential configurations for authentication to BigQuery services. During connector configuration, users can supply credential JSON files that are processed by Google authentication libraries. The service fails to validate externally-sourced credential configurations before passing them to the authentication libraries. An attacker can exploit this by providing a malicious credential configuration containing crafted credential_source.file paths or credential_source.url endpoints, resulting in arbitrary file reads or SSRF attacks.

## References
- https://docs.cloud.google.com/support/bulletins#gcp-2025-005
- https://github.com/Aiven-Open/bigquery-connector-for-apache-kafka/releases/tag/v2.11.0
- https://github.com/Aiven-Open/bigquery-connector-for-apache-kafka/security/advisories/GHSA-3mg8-2g53-5gj4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23529.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23529
- https://github.com/Aiven-Open/bigquery-connector-for-apache-kafka/commit/20ea3921c6fe72d605a033c1943b20f49eaba981
