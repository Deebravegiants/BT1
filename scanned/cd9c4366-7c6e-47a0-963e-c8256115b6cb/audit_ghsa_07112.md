# [M] Apache Camel-Elasticsearch-Rest-Client: Exchange header constants without the Camel prefix bypass inbound HTTP header filtering, allowing untrusted clients to override the Elasticsearch query and operation

## Summary
Severity: Medium
Advisory: GHSA-rp9m-hfv5-pfvr
CVE: CVE-2026-46453
CWE: CWE-20, CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-rp9m-hfv5-pfvr
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-elasticsearch-rest-client` — affected >=4.3.0 <4.14.8
- Maven: `org.apache.camel:camel-elasticsearch-rest-client` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-elasticsearch-rest-client` — affected >=4.19.0 <4.21.0

## Details
Improper Input Validation, Authorization Bypass Through User-Controlled Key vulnerability in Apache Camel ElasticSearch Rest Client.

The camel-elasticsearch-rest-client component reads several Exchange headers to control its behaviour - SEARCH_QUERY (an advanced query body), OPERATION (which Elasticsearch operation to run), INDEX_NAME, INDEX_SETTINGS and ID. The string values of these header constants, defined in ElasticSearchRestClientConstant, are plain unprefixed names ('SEARCH_QUERY', 'OPERATION', 'INDEX_NAME', 'INDEX_SETTINGS', 'ID') rather than the 'Camel'-prefixed names used by every other Camel component (for example CamelSqlQuery, CamelMongoDbCriteria, CamelCqlQuery). Camel's inbound HTTP header filter, HttpHeaderFilterStrategy, blocks only header names that begin with 'Camel' or 'camel'. Because the Elasticsearch header names do not carry that prefix, they pass through the inbound filter unchanged. When a Camel route exposes an HTTP entry point (for example platform-http) in front of an elasticsearch-rest-client producer, an untrusted HTTP client can set these headers directly on its request and override the query and operation that the route author configured: reading every document in the index (SEARCH_QUERY with a match_all query), deleting documents (OPERATION set to Delete together with ID), or exfiltrating selected fields. No credentials are required and the producer reads the headers unconditionally.
This issue affects Apache Camel: from 4.3.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.8. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. The fix renames the camel-elasticsearch-rest-client Exchange header constant string values (ID, SEARCH_QUERY, INDEX_SETTINGS, INDEX_NAME, OPERATION) to carry the Camel prefix (CamelElasticsearchId, CamelElasticsearchSearchQuery, CamelElasticsearchIndexSettings, CamelElasticsearchIndexName, CamelElasticsearchOperation) so that they are blocked by the inbound HttpHeaderFilterStrategy; the Java field names are unchanged. For deployments that cannot upgrade immediately, strip the affected headers from untrusted inbound messages before they reach the producer (for example removeHeader('SEARCH_QUERY'), removeHeader('OPERATION'), removeHeader('INDEX_NAME'), removeHeader('INDEX_SETTINGS') and removeHeader('ID') in front of the elasticsearch-rest-client endpoint), or apply a custom HeaderFilterStrategy that blocks these names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46453
- https://github.com/apache/camel/pull/23212
- https://github.com/apache/camel/pull/23244
- https://github.com/apache/camel/commit/0a87d31c8d19f59da4a5477bde192cc258ecc5d7
- https://github.com/apache/camel/commit/81f3a625c8853d6dff5fd748a0da9dba259c4076
- https://github.com/apache/camel/commit/ff88400e3a95af16e17d553b34d3752d96496c5d
- https://camel.apache.org/security/CVE-2026-46453.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.8
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23508
- http://www.openwall.com/lists/oss-security/2026/07/05/6
