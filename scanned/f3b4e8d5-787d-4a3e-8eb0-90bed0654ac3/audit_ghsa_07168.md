# [M] OpenTelemetry Javaagent RMI context propagation allows resource exhaustion

## Summary
Severity: Medium
Advisory: GHSA-fq3f-m5qm-99f5
CVE: CVE-2026-54712
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-fq3f-m5qm-99f5
Type: github-advisory

## Affected
- Maven: `io.opentelemetry.javaagent:opentelemetry-javaagent` — affected >=0 <2.27.0

## Details
The RMI context propagation payload reader limits the number of context entries but does not limit the aggregate size of the strings read from the stream.

An attacker who can reach an RMI endpoint on an instrumented JVM can send an oversized context propagation payload. This can cause excessive memory allocation while the JVM reads the payload, potentially leading to denial of service.

The issue affects only deployments where RMI instrumentation is enabled and an RMI endpoint is network-reachable.

## References
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/security/advisories/GHSA-fq3f-m5qm-99f5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54712
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/pull/17870
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/commit/6ef18806d5daa4913619e4cb33d2d7ed6a853c22
- https://github.com/open-telemetry/opentelemetry-java-instrumentation
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/tag/v2.27.0
