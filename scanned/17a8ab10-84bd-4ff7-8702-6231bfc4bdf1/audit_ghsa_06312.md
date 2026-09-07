# [M] OpenTelemetry-Go: Unsynchronized baggage map can panic under concurrent access

## Summary
Severity: Medium
Advisory: GHSA-42cj-99w8-cp2p
CVE: CVE-2026-45404
CWE: CWE-362, CWE-667
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-42cj-99w8-cp2p
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/otel/bridge/opentracing` — affected >=0.11.0 <1.45.0

## Details
### Summary

`go.opentelemetry.io/otel/bridge/opentracing` introduced an unsynchronized `extraBaggageItems` map on `bridgeSpan`. One goroutine can write this map through `Span.SetBaggageItem` while another goroutine reads and iterates it during correlation baggage propagation, which can trigger Go's fatal concurrent map access panic and crash the process. The finding is low severity because exploitation requires a specific OpenTracing bridge configuration and concurrent use of the same span.

Introduced in commit: 8cddf30

### Details

`bridge/opentracing/bridge.go:80-85` adds `extraBaggageItems map[string]string` to `bridgeSpan` without a mutex or other synchronization primitive. `bridge/opentracing/bridge.go:219-234` shows `SetBaggageItem` calling `updateOtelContext`, which lazily creates the map and writes `s.extraBaggageItems[restrictedKey] = value` without locking. `bridge/opentracing/bridge.go:359-377` shows `correlationGetHook` reading `bSpan.extraBaggageItems`, checking `len(items)`, and iterating `for k, v := range items` without locking. The finding evidence also identifies `api/correlation/context.go:160-165` as the path where `correlation.MapFromContext` invokes the get hook, allowing a read path to run concurrently with baggage writes.

Because Go maps are not safe for concurrent read/write access, concurrent `SetBaggageItem` and `correlation.MapFromContext` calls on the same hooked `bridgeSpan` can terminate the process with a runtime error such as `fatal error: concurrent map read and map write` or `fatal error: concurrent map iteration and map write`.

### PoC

[validation-artifact.zip](https://github.com/user-attachments/files/27494614/validation-artifact.zip)


The validation artifact contains a PoC at `validation-artifact.tar:validation_poc_concurrent_map.go` and supporting notes at `validation-artifact.tar:validation_poc_README.txt`.

Use a checkout of `pellared/opentelemetry-go` at commit `8cddf30` with Go module downloads enabled. The local validation environment could not complete the run because `GOPROXY=off` blocked dependency resolution; that blocked output is saved in `validation-artifact.tar:validation_poc_run.log`.

Commands:

```sh
cd /path/to/opentelemetry-go
git checkout 8cddf30
tar -xOf /path/to/finding-directory/validation-artifact.tar validation_poc_concurrent_map.go > ./validation_poc_concurrent_map.go
GOPROXY=https://proxy.golang.org,direct go run ./validation_poc_concurrent_map.go
```

The PoC starts a `BridgeTracer`, creates a span, installs correlation hooks with `tracer.NewHookedContext(ctx)`, initializes baggage once, then runs one goroutine repeatedly calling `span.SetBaggageItem(...)` while another repeatedly calls `otelcorrelation.MapFromContext(ctx)`. A vulnerable build is expected to terminate with a Go runtime concurrent map access error, for example:

```text
fatal error: concurrent map read and map write
```

or:

```text
fatal error: concurrent map iteration and map write
```


### Impact

This is a race condition / improper synchronization vulnerability in a shared Go map. Applications using the OpenTelemetry OpenTracing bridge with correlation hooks can crash if the same `bridgeSpan` is accessed concurrently, with one execution path setting baggage and another propagating correlation baggage. The practical impact is denial of service for the affected application process; exposure depends on whether application request handling or internal concurrency can trigger those operations on the same span.

## References
- https://github.com/open-telemetry/opentelemetry-go/security/advisories/GHSA-42cj-99w8-cp2p
- https://github.com/open-telemetry/opentelemetry-go/pull/8693
- https://github.com/open-telemetry/opentelemetry-go/commit/93a693edeed0e07ce5ebd1dfe67af42d1e2055d8
- https://github.com/open-telemetry/opentelemetry-go
- https://github.com/open-telemetry/opentelemetry-go/releases/tag/v1.45.0
