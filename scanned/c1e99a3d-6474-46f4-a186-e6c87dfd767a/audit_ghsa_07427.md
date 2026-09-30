# [M] OpenTelemetry Java Instrumentation: JDBC Auto-Instrumentation Logging Clear-Text Passwords

## Summary
Severity: Medium
Advisory: GHSA-rwqx-fvqh-6wm4
CVE: CVE-2026-54704
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-rwqx-fvqh-6wm4
Type: github-advisory

## Affected
- Maven: `io.opentelemetry.javaagent:opentelemetry-javaagent` — affected >=0 <2.28.0-alpha

## Details
OpenTelemetry Java Instrumentation JDBC auto-instrumentation may fail to sanitize passwords in SQL CONNECT statements when the password is double-quoted. As a result, clear-text database passwords can be added to trace span attributes and exported to observability backends.

## References
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/security/advisories/GHSA-rwqx-fvqh-6wm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-54704
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/pull/18754
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/commit/7ac7fa6fda6c2e3b65bc5d3c6eba050311a49511
- https://github.com/open-telemetry/opentelemetry-java-instrumentation
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/tag/v2.28.0
