# [M] OpenSearch Data Prepper uses deprecated SSL protocol identifier

## Summary
Severity: Medium
Advisory: GHSA-28gg-8qqj-fhh5
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-28gg-8qqj-fhh5
Type: github-advisory

## Affected
- Maven: `org.opensearch.dataprepper.plugins:geoip-processor` — affected >=2.4.0 <2.12.2

## Details
### Impact

The GeoIP processor and Kafka source and buffer were using the deprecated "SSL" protocol identifier when creating SSL contexts, potentially allowing the use of insecure SSL protocols instead of modern TLS versions.

Multiple Data Prepper plugins used `SSLContext.getInstance("SSL")` which could potentially allow the use of deprecated SSL protocols (SSLv2, SSLv3) that have known security vulnerabilities. While modern Java implementations typically default to secure TLS versions even with the "SSL" identifier, explicitly using "TLS" ensures that only secure TLS protocols are negotiated.

The affected components were:

* GeoIP Processor: The `DBSource.initiateSSL()` method used for downloading GeoIP databases from external sources

* Kafka Plugin: Both `CustomClientSslEngineFactory` and `InsecureSslEngineFactory` classes used for Kafka client connections

This could potentially allow connections to negotiate weaker SSL protocols instead of enforcing modern TLS versions, reducing the security of data transmission.

### Patches

Data Prepper 2.12.2 contains a fix for this issue.

### Workarounds

If upgrading is not immediately possible:

1. Ensure your Java runtime is configured to disable deprecated SSL protocols
2. Use network-level controls to enforce TLS-only connections
3. Use external tools to verify that deprecated SSL protocols are not allowed.

## References
- https://github.com/opensearch-project/data-prepper/security/advisories/GHSA-28gg-8qqj-fhh5
- https://github.com/opensearch-project/data-prepper/commit/fa21a601512b5193c4b5c84a5b30c6301dab0475
- https://github.com/opensearch-project/data-prepper
