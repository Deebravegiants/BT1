# [C] Apache Camel has an incomplete fix for CVE-2025-27636

## Summary
Severity: Critical
Advisory: GHSA-jg2m-9x48-3gvj
CVE: CVE-2026-40453
CWE: CWE-178
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-jg2m-9x48-3gvj
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-coap` — affected >=3.0.0 <4.14.6
- Maven: `org.apache.camel:camel-coap` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-coap` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-google-pubsub` — affected >=3.0.0 <4.14.6
- Maven: `org.apache.camel:camel-google-pubsub` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-google-pubsub` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-jms` — affected >=3.0.0 <4.14.6
- Maven: `org.apache.camel:camel-jms` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-jms` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-sjms` — affected >=3.0.0 <4.14.6
- Maven: `org.apache.camel:camel-sjms` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-sjms` — affected >=4.19.0 <4.20.0

## Details
The fix for CVE-2025-27636 added setLowerCase(true) to HttpHeaderFilterStrategy so that case-variant header names such as 'CAmelExecCommandExecutable' are filtered out alongside 'CamelExecCommandExecutable'. The same setLowerCase(true) call was not applied to five non-HTTP HeaderFilterStrategy implementations: JmsHeaderFilterStrategy and ClassicJmsHeaderFilterStrategy in camel-jms, SjmsHeaderFilterStrategy in camel-sjms, CoAPHeaderFilterStrategy in camel-coap, and GooglePubsubHeaderFilterStrategy in camel-google-pubsub. Because those strategies use case-sensitive String.startsWith('Camel'/'camel') filtering while the Camel Exchange stores headers in a case-insensitive map, an attacker with JMS (or equivalent) producer access to the broker consumed by a Camel route can inject case-variant Camel internal headers, which are then resolved by downstream components such as camel-exec and camel-file using their canonical casing. This enables remote code execution and arbitrary file write on routes that forward JMS messages to header-driven components.

This issue affects Apache Camel: from 3.0.0 before 4.14.6, from 4.15.0 before 4.18.2, from 4.19.0 before 4.20.0.

Users are recommended to upgrade to version 4.20.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.6. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40453
- https://github.com/apache/camel/pull/22569
- https://github.com/apache/camel/pull/22575
- https://github.com/apache/camel/pull/22576
- https://github.com/apache/camel/commit/1e331daa4eea0a3f01d951e74cda8faee79495a2
- https://github.com/apache/camel/commit/301bb7401cd480895b94a28a8ad6cf04952d8125
- https://github.com/apache/camel/commit/3d2efeed2f6ea757f0254a1d1cdeb9a4f28ca147
- https://camel.apache.org/security/CVE-2026-40453.html
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-23313
