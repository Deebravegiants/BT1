# [C] OpenTelemetry: Unsafe Deserialization in RMI Instrumentation may Lead to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-xw7x-h9fj-p2c7
CVE: CVE-2026-33701
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-xw7x-h9fj-p2c7
Type: github-advisory

## Affected
- Maven: `io.opentelemetry.javaagent:opentelemetry-javaagent` — affected >=0 <2.26.1

## Details
In versions prior to 2.26.1, the RMI instrumentation registered a custom endpoint that deserialized incoming data without applying serialization filters. An attacker with network access to a JMX or RMI port on an instrumented JVM could exploit this to potentially achieve remote code execution. All three of the following conditions must be true to exploit this vulnerability:
1. OpenTelemetry Java instrumentation is attached as a Java agent (`-javaagent`)
2. An RMI endpoint is network-reachable (e.g. JMX remote port, an RMI registry, or any application-exported RMI service)
3. A gadget-chain-compatible library is present on the classpath

### Impact
Arbitrary remote code execution with the privileges of the user running the instrumented JVM.

### Recommendation
Upgrade to version 2.26.1 or later.

### Workarounds
Set the following system property to disable the RMI integration:

```
-Dotel.instrumentation.rmi.enabled=false
```

### Credits
This vulnerability was responsibly disclosed in coordination with Datadog.

## References
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/security/advisories/GHSA-xw7x-h9fj-p2c7
- https://nvd.nist.gov/vuln/detail/CVE-2026-33701
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/commit/9cf4fbaaa9e79226142b2ed42a6f6b4ac0be2197
- https://access.redhat.com/security/cve/CVE-2026-33701
- https://bugzilla.redhat.com/show_bug.cgi?id=2452071
- https://github.com/open-telemetry/opentelemetry-java-instrumentation
- https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/tag/v2.26.1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33701.json
