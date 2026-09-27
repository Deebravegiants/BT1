# [M] KQL injection via kusto.tables.topics.mapping in kafka-sink-azure-kusto

## Summary
Severity: Medium
Advisory: CVE-2026-42316
Aliases: GHSA-c9mr-mqvh-6wgj
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N/E:P/RL:O/RC:C)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42316
Type: osv

## Details
kafka-sink-azure-kusto Kafka Connect plugin is the official Microsoft sink for Azure Data Explorer (Kusto). Prior to 5.2.3, kafka-sink-azure-kusto did not sanitize user-controlled values inside the kusto.tables.topics.mapping configuration. The db, table, mapping, and format fields of each mapping entry were interpolated directly into KQL management/query commands via String.formatted(...) (e.g., FETCH_TABLE_COMMAND.formatted(table) → "<table> | count", FETCH_TABLE_MAPPING_COMMAND.formatted(table, format, mapping) → ".show table <table> ingestion <format> mapping '<mapping>'"). An actor able to influence the connector configuration (for example, someone with permissions to submit or edit Kafka Connect connector configs) could embed KQL metacharacters (;, |, ') to execute arbitrary management commands in the context of the connector's service principal — enabling schema enumeration/modification, ingestion-mapping tampering, or changes to streaming/retention policies on the target Azure Data Explorer database. This is a tampering vulnerability. Exploitation requires privileged access to the connector configuration; no end-user interaction or Kafka record payload is involved. This vulnerability is fixed in 5.2.3.

## References
- https://github.com/Azure/kafka-sink-azure-kusto/releases/tag/v5.2.3
- https://github.com/Azure/kafka-sink-azure-kusto/security/advisories/GHSA-c9mr-mqvh-6wgj
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42316.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42316
- https://github.com/Azure/kafka-sink-azure-kusto/pull/155
