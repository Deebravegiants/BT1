# [C] Apache Camel-Atmosphere-Websocket: WebSocket dispatch header injection - the producer selected its target peers through Exchange headers whose names sat outside the filtered Camel namespace

## Summary
Severity: Critical
Advisory: GHSA-m5r8-w65q-8wjf
CVE: CVE-2026-71300
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-m5r8-w65q-8wjf
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-atmosphere-websocket` — affected >=4.0.0 <4.14.9
- Maven: `org.apache.camel:camel-atmosphere-websocket` — affected >=4.15.0 <4.18.4
- Maven: `org.apache.camel:camel-atmosphere-websocket` — affected >=4.19.0 <4.22.0

## Details
Improper input validation vulnerability in Apache Camel Atmosphere Websocket component.

This issue affects Apache Camel: from 4.0.0 before 4.14.9, from 4.15.0 before 4.18.4, from 4.19.0 before 4.22.0.

The camel-atmosphere-websocket producer selects which connected WebSocket peers a message is delivered to through Exchange headers, and the string values of those headers sat outside the Camel namespace: websocket.connectionKey and websocket.connectionKey.list, along with websocket.sendToAll, websocket.eventType and websocket.errorType. WebsocketEndpoint extends ServletEndpoint and so inherits HttpHeaderFilterStrategy, which filters only the Camel and camel prefixes; the dotted names therefore fell outside the filtered namespace and were admitted in both directions by every HTTP-family consumer. In a route bridging an HTTP consumer into an atmosphere-websocket producer, an external sender could supply the list header and take over the producer's dispatch decision. WebsocketProducer.process tests the list header before the single-key header, so an injected value discarded the recipient the route had selected: a notification intended for one connected client could be suppressed, or delivered instead to a different client whose connection key the sender knows. The header need not be a query parameter and need not be supplied as a list literally - Camel's HTTP binding promotes a repeated header name, and a bracketed value, to a List when mapping onto the Exchange - so an ordinary inbound HTTP header is sufficient to reach the list-valued branch. This is distinct from CVE-2026-55993, which concerns the consumer-side query-parameter path in the same component. The behaviour dates back to the introduction of these constants, first released in 2.17.0, and was unchanged until this fix.

Users are recommended to upgrade to version 4.22.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.9. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.4. For deployments that cannot upgrade immediately, strip the dispatch headers at the trust boundary before the producer, for example with removeHeaders(“websocket.*”) placed between the HTTP consumer and the atmosphere-websocket producer. Note that the fix renames the header string values into the Camel namespace, which is a breaking change for routes that set them by literal string: routes referencing the WebsocketConstants fields symbolically are unaffected, and the change is documented in the upgrade guides. As defence in depth, do not bridge an untrusted HTTP consumer directly into a WebSocket producer whose dispatch is header-driven without stripping the dispatch namespace first.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-71300
- https://github.com/apache/camel/pull/25366
- https://github.com/apache/camel/pull/25382
- https://github.com/apache/camel/pull/25383
- https://github.com/apache/camel/pull/25384
- https://github.com/apache/camel/commit/49e197a66158eb7151b461b46b37407df2e13591
- https://github.com/apache/camel/commit/60ca704c0379e6e87107158c0b2174c3f0f2f48a
- https://github.com/apache/camel/commit/66567833fb1efe6d66c6618dbb48295cce4c84ba
- https://camel.apache.org/security/CVE-2026-71300.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.9
- https://github.com/apache/camel/releases/tag/camel-4.18.4
- https://github.com/apache/camel/releases/tag/camel-4.22.0
- https://issues.apache.org/jira/browse/CAMEL-24359
