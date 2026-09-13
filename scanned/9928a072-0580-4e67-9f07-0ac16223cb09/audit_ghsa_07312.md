# [M] Apache Camel-Dapr: The Dapr Pub/Sub consumer copied the inbound CloudEvent's pub/sub-name and topic into producer-direction routing headers

## Summary
Severity: Medium
Advisory: GHSA-583r-f84w-33g7
CVE: CVE-2026-49086
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-583r-f84w-33g7
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-dapr` — affected >=4.12.0 <4.14.8
- Maven: `org.apache.camel:camel-dapr` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-dapr` — affected >=4.19.0 <4.21.0

## Details
Improper Input Validation, Unintended Proxy or Intermediary ('Confused Deputy') vulnerability in Apache Camel DAPR component.

The camel-dapr Dapr Pub/Sub consumer (DaprPubSubConsumer) copied two fields from each inbound CloudEvent - its Pub/Sub component name and its topic - into the CamelDaprPubSubName and CamelDaprTopic Exchange headers. These two headers are producer-direction routing headers: when the route republishes through a Dapr producer, DaprConfigurationOptionsProxy reads them back and prefers them over the destination configured on the endpoint. As a result, in a route that consumes from one Dapr Pub/Sub topic and republishes to another (for example from('dapr-pubsub:p:t').to('dapr-pubsub:p:other')), an actor able to publish a message to the subscribed topic could set the CloudEvent's pub/sub-name and topic to values of their choosing and cause the re-published message to be delivered to an arbitrary Dapr Pub/Sub component and topic instead of the configured destination - redirecting or exfiltrating the message and bypassing the route's intended routing and any topic-level access controls in the underlying broker. Exploitation requires the ability to publish to the topic the route subscribes to; no other authentication or user interaction is needed.
This issue affects Apache Camel: from 4.12.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.8. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. For deployments that cannot upgrade immediately, remove the CamelDaprPubSubName and CamelDaprTopic headers from the Exchange between the Dapr consumer and any Dapr producer in the route (for example removeHeaders('CamelDaprPubSubName', 'CamelDaprTopic')), and restrict who can publish to the subscribed Dapr Pub/Sub topic so that only trusted producers can send to it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49086
- https://github.com/apache/camel/pull/23886
- https://github.com/apache/camel/pull/23889
- https://github.com/apache/camel/pull/23905
- https://github.com/apache/camel/commit/72d13bd13fb5960ea1b367a2e379f017c1720c5c
- https://github.com/apache/camel/commit/86276a2ccc2cf8b09d7efeb38d9770845c4e1bea
- https://github.com/apache/camel/commit/c6fc9bb21670e5c65ea14df0f3f29baef78c2028
- https://camel.apache.org/security/CVE-2026-49086.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.8
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23630
- http://www.openwall.com/lists/oss-security/2026/07/05/21
