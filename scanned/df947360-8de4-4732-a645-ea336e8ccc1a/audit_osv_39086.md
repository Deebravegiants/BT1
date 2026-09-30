# [H] Apache Camel: Camel-Hazelcast: Unsafe Java deserialization in default-configured managed Hazelcast instances enables remote code execution

## Summary
Severity: High
Advisory: CVE-2026-43865
Aliases: GHSA-xww8-mxqw-m84w
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-43865
Type: osv

## Details
Deserialization of Untrusted Data vulnerability in Apache Camel Hazelcast component.

The camel-hazelcast component creates and manages Hazelcast instances using a default configuration that applies no Java deserialization filter. When Camel builds the Hazelcast Config itself - that is, when no user-supplied HazelcastInstance, hazelcastConfigUri, or referenced Config bean is provided - neither Hazelcast's JavaSerializationFilterConfig nor a Camel-side ObjectInputFilter is configured, so objects received over the Hazelcast cluster protocol are deserialized inside Hazelcast's own serialization layer (ObjectInputStream.readObject) before Camel ever processes them. An attacker who can join or otherwise reach the Hazelcast cluster can publish a crafted serialized Java object that is then deserialized on every Camel node, resulting in remote code execution. The exposure is present by default and requires no opt-in endpoint configuration: any route using a hazelcast consumer (hazelcast-topic, hazelcast-queue, hazelcast-seda, hazelcast-map, hazelcast-multimap, hazelcast-replicatedmap, hazelcast-list, hazelcast-set), as well as the HazelcastAggregationRepository and HazelcastIdempotentRepository, is affected whenever the managed instance is created from Camel's default configuration.
This issue affects Apache Camel: from 4.0.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.8. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. The fix makes Camel apply a default Hazelcast JavaSerializationFilterConfig (whitelisting the java., javax. and org.apache.camel. class-name prefixes and blacklisting java.net.) to instances it creates from its own default configuration, while leaving any user-supplied Config or HazelcastInstance untouched. For deployments that cannot upgrade immediately, configure a deserialization filter on the Hazelcast instance (Hazelcast JavaSerializationFilterConfig, or the JVM-wide system property -Djdk.serialFilter=!java.net.**;java.**;javax.**;org.apache.camel.**;!*) and enable Hazelcast cluster authentication and TLS to restrict who can reach the cluster.

## References
- http://www.openwall.com/lists/oss-security/2026/07/05/5
- https://repo.maven.apache.org/maven2
- https://camel.apache.org/security/CVE-2026-43865.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43865.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43865
