# [M] OpenTelemetry eBPF Instrumentation: Redis error text is exported in span status messages

## Summary
Severity: Medium
Advisory: GHSA-8rrq-wcg8-cv5q
CVE: CVE-2026-45679
CWE: CWE-117, CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-8rrq-wcg8-cv5q
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0 <0.9.0

## Details
### Summary

OBI exports raw Redis error text as the span status message. Because Redis error replies can contain attacker-controlled or sensitive values, this behavior can exfiltrate tokens, PII, or other confidential input into telemetry backends and inject untrusted text into downstream analysis systems.

### Details

In [pkg/ebpf/common/redis_detect_transform.go](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/4f35facce2fe611319672595838ab875490f404d/pkg/components/ebpf/common/redis_detect_transform.go#L60-L74), `getRedisError` trims the raw error buffer and stores it directly in `request.DBError.Description`.

Later, [pkg/appolly/app/request/span.go](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/4f35facce2fe611319672595838ab875490f404d/pkg/app/request/span.go#L347-L352) returns that description as the exported status message for Redis spans whenever the span status is non-zero.

There is no opt-in control or sanitization beyond CRLF trimming. As a result, raw Redis error text becomes part of OTLP-exported status metadata by default.

### PoC

Local request-layer testing recorded a status message containing `ERR invalid password for user bob secret=TOPSECRET`, which shows that unfiltered Redis error text reaches the exported status message.

Use a vulnerable build:

```bash
git checkout v0.0.0-rc.1+build
make build
```

Start Redis and OBI:

```bash
docker run --rm -p 6379:6379 redis:7
sudo ./bin/obi
```

Send a command that causes Redis to return an error containing caller-supplied text:

```bash
redis-cli -p 6379 'NOTACMD my-secret-token-123'
```

Capture the exported span or inspect the local telemetry output. On a vulnerable build, the span status message contains the Redis error text, including the supplied command fragment. This demonstrates that raw Redis error text is exported into telemetry by default and that values embedded in that text, including data supplied unintentionally by a caller, can be carried into tracing systems.

### Impact

This is an information disclosure and telemetry injection issue. It affects any deployment that traces Redis traffic and exports spans to collectors, logs, or dashboards. Sensitive values, tokens, or PII present in Redis error text can be exfiltrated into telemetry systems, and untrusted text can contaminate downstream analysis.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-8rrq-wcg8-cv5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-45679
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
