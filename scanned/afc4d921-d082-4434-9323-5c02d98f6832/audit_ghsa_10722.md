# [M] opentelemetry-go: OTLP HTTP exporters read unbounded HTTP response bodies

## Summary
Severity: Medium
Advisory: GHSA-w8rr-5gcm-pp58
CVE: CVE-2026-39882
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-w8rr-5gcm-pp58
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp` — affected >=0 <1.43.0
- Go: `go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp` — affected >=0 <1.43.0
- Go: `go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploghttp` — affected >=0 <0.19.0

## Details
overview:
this report shows that the otlp HTTP exporters (traces/metrics/logs) read the full HTTP response body into an in-memory `bytes.Buffer` without a size cap.

this is exploitable for memory exhaustion when the configured collector endpoint is attacker-controlled (or a network attacker can mitm the exporter connection).

severity

HIGH

not claiming: this is a remote dos against every default deployment.
claiming: if the exporter sends traces to an untrusted collector endpoint (or over a network segment where mitm is realistic), that endpoint can crash the process via a large response body.

callsite (pinned):
- exporters/otlp/otlptrace/otlptracehttp/client.go:199
- exporters/otlp/otlptrace/otlptracehttp/client.go:230
- exporters/otlp/otlpmetric/otlpmetrichttp/client.go:170
- exporters/otlp/otlpmetric/otlpmetrichttp/client.go:201
- exporters/otlp/otlplog/otlploghttp/client.go:190
- exporters/otlp/otlplog/otlploghttp/client.go:221

permalinks (pinned):
- https://github.com/open-telemetry/opentelemetry-go/blob/248da958375e4dfb4a1105645107be3ef04b1c59/exporters/otlp/otlptrace/otlptracehttp/client.go#L199
- https://github.com/open-telemetry/opentelemetry-go/blob/248da958375e4dfb4a1105645107be3ef04b1c59/exporters/otlp/otlptrace/otlptracehttp/client.go#L230
- https://github.com/open-telemetry/opentelemetry-go/blob/248da958375e4dfb4a1105645107be3ef04b1c59/exporters/otlp/otlpmetric/otlpmetrichttp/client.go#L170
- https://github.com/open-telemetry/opentelemetry-go/blob/248da958375e4dfb4a1105645107be3ef04b1c59/exporters/otlp/otlpmetric/otlpmetrichttp/client.go#L201
- https://github.com/open-telemetry/opentelemetry-go/blob/248da958375e4dfb4a1105645107be3ef04b1c59/exporters/otlp/otlplog/otlploghttp/client.go#L190
- https://github.com/open-telemetry/opentelemetry-go/blob/248da958375e4dfb4a1105645107be3ef04b1c59/exporters/otlp/otlplog/otlploghttp/client.go#L221

root cause:
each exporter client reads `resp.Body` using `io.Copy(&respData, resp.Body)` into a `bytes.Buffer` on both success and error paths, with no upper bound.

impact:
a malicious collector can force large transient heap allocations during export (peak memory scales with attacker-chosen response size) and can potentially crash the instrumented process (oom).

affected component:
- go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp
- go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp
- go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploghttp

repro (local-only):

```bash
unzip poc.zip -d poc
cd poc
make canonical resp_bytes=33554432 chunk_delay_ms=0
```

expected output contains:

```
[CALLSITE_HIT]: otlptracehttp.UploadTraces::io.Copy(resp.Body)
[PROOF_MARKER]: resp_bytes=33554432 peak_alloc_bytes=118050512
```

control (same env, patched target):

```bash
unzip poc.zip -d poc
cd poc
make control resp_bytes=33554432 chunk_delay_ms=0
```

expected control output contains:

```
[CALLSITE_HIT]: otlptracehttp.UploadTraces::io.Copy(resp.Body)
[NC_MARKER]: resp_bytes=33554432 peak_alloc_bytes=512232
```

attachments: poc.zip (attached)

[PR_DESCRIPTION.md](https://github.com/user-attachments/files/25564272/PR_DESCRIPTION.md)

[attack_scenario.md](https://github.com/user-attachments/files/25564273/attack_scenario.md)

[poc.zip](https://github.com/user-attachments/files/25564271/poc.zip)


Fixed in: https://github.com/open-telemetry/opentelemetry-go/pull/8108

## References
- https://github.com/open-telemetry/opentelemetry-go/security/advisories/GHSA-w8rr-5gcm-pp58
- https://nvd.nist.gov/vuln/detail/CVE-2026-39882
- https://github.com/open-telemetry/opentelemetry-go/pull/8108
- https://github.com/open-telemetry/opentelemetry-go
- http://github.com/open-telemetry/opentelemetry-go/releases/tag/v1.43.0
