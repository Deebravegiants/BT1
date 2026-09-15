# [C] Camel-CXF and Camel-Knative Message Header are Vulnerable to Injection via Missing Inbound Filtering

## Summary
Severity: Critical
Advisory: GHSA-8364-hfqj-pwm6
CVE: CVE-2026-47323
CWE: CWE-178
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-8364-hfqj-pwm6
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-cxf-rest` — affected >=3.18.0 <4.14.6
- Maven: `org.apache.camel:camel-cxf-rest` — affected >=4.15.0 <4.18.2

## Details
Camel-CXF and Camel-Knative Message Header Injection via Missing Inbound Filtering

The CXF and Knative HeaderFilterStrategy implementations (CxfRsHeaderFilterStrategy in camel-cxf-rest, CxfHeaderFilterStrategy in camel-cxf-transport, and KnativeHttpHeaderFilterStrategy in camel-knative-http) only filter outbound Camel-internal headers via setOutFilterStartsWith, while not configuring inbound filtering via setInFilterStartsWith. As a result, an unauthenticated attacker can inject Camel-internal headers (e.g. CamelExecCommandExecutable, CamelFileName) via HTTP requests to CXF-RS or CXF-SOAP endpoints. When a route forwards messages from these endpoints to header-driven components such as camel-exec or camel-file, the injected headers override configured values, enabling remote code execution or arbitrary file writes. This is the same pattern that was previously addressed in camel-undertow (CVE-2025-30177), the broader incoming-header filter (CVE-2025-27636 and CVE-2025-29891), and non-HTTP strategies (CVE-2026-40453).


This issue affects Apache Camel: from 3.18.0 before 4.14.6, from 4.15.0 before 4.18.2.

Users are recommended to upgrade to version 4.19.0, which fixes the issue. If users are on the 4.18.x LTS releases stream, then they are suggested to upgrade to 4.18.2. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-47323
- https://camel.apache.org/security/CVE-2026-47323.html
- https://github.com/apache/camel
