# [M] Apache Pulsar: Improper Authorization For Namespace and Topic Management Endpoints

## Summary
Severity: Medium
Advisory: GHSA-7mg2-6c6v-342r
CVE: CVE-2024-29834
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-02
Source: https://github.com/advisories/GHSA-7mg2-6c6v-342r
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.7.1
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.11.0
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=3.0.0 <3.0.4
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=3.1.0
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=3.2.0 <3.2.2

## Details
This vulnerability allows authenticated users with produce or consume permissions to perform unauthorized operations on partitioned topics, such as unloading topics and triggering compaction. These management operations should be restricted to users with the tenant admin role or superuser role. An authenticated user with produce permission can create subscriptions and update subscription properties on partitioned topics, even though this should be limited to users with consume permissions. This impact analysis assumes that Pulsar has been configured with the default authorization provider. For custom authorization providers, the impact could be slightly different. Additionally, the vulnerability allows an authenticated user to read, create, modify, and delete namespace properties in any namespace in any tenant. In Pulsar, namespace properties are reserved for user provided metadata about the namespace.

This issue affects Apache Pulsar versions from 2.7.1 to 2.10.6, from 2.11.0 to 2.11.4, from 3.0.0 to 3.0.3, from 3.1.0 to 3.1.3, and from 3.2.0 to 3.2.1. 

3.0 Apache Pulsar users should upgrade to at least 3.0.4.
3.1 and 3.2 Apache Pulsar users should upgrade to at least 3.2.2.

Users operating versions prior to those listed above should upgrade to the aforementioned patched versions or newer versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29834
- https://github.com/apache/pulsar/commit/6ffe667cddad3e959e02ce31fd09b2f9a439d50a
- https://github.com/apache/pulsar/commit/b51b74883fb66673161d0b73c6a7257d073c57a5
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/v0ltl94k9lg28qfr1f54hpkvvsjc5bj5
- https://pulsar.apache.org/security/CVE-2024-29834
- http://www.openwall.com/lists/oss-security/2024/04/02/2
