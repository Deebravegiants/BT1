# [H] OpenTelemetry-Go: multi-value `baggage` header extraction causes excessive allocations (remote dos amplification)

## Summary
Severity: High
Advisory: GHSA-mh2q-q3fh-2475
CVE: CVE-2026-29181
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-mh2q-q3fh-2475
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/otel` — affected >=1.36.0 <1.41.0

## Details
multi-value `baggage:` header extraction parses each header field-value independently and aggregates members across values. this allows an attacker to amplify cpu and allocations by sending many `baggage:` header lines, even when each individual value is within the 8192-byte per-value parse limit.

## severity

HIGH (availability / remote request amplification)

## relevant links

- repository: https://github.com/open-telemetry/opentelemetry-go
- pinned callsite: https://github.com/open-telemetry/opentelemetry-go/blob/1ee4a4126dbdd1bc79e9fae072fa488beffac52a/propagation/baggage.go#L58

## vulnerability details

**pins:** open-telemetry/opentelemetry-go@1ee4a4126dbdd1bc79e9fae072fa488beffac52a
**as-of:** 2026-02-04
**policy:** direct (no program scope provided)

**callsite:** propagation/baggage.go:58 (`extractMultiBaggage`)
**attacker control:** inbound HTTP request headers (many `baggage` field-values) → `propagation.HeaderCarrier.Values("baggage")` → repeated `baggage.Parse` + member aggregation

### root cause

`extractMultiBaggage` iterates over all `baggage` header field-values and parses each one independently, then appends members into a shared slice. the 8192-byte parsing cap applies per header value, but the multi-value path repeats that work once per header line (bounded only by the server/proxy header byte limit).

### impact

in a default `net/http` configuration (max header bytes 1mb), a single request with many `baggage:` header field-values can cause large per-request allocations and increased latency.

example from the attached PoC harness (darwin/arm64; 80 values; 40 requests):

- canonical: `per_req_alloc_bytes=10315458` and `p95_ms=7`
- control: `per_req_alloc_bytes=133429` and `p95_ms=0`

## proof of concept

canonical:

```bash
mkdir -p poc
unzip poc.zip -d poc
cd poc
make test
```

output (excerpt):

```
[CALLSITE_HIT]: propagation/baggage.go:58 extractMultiBaggage
[PROOF_MARKER]: baggage_multi_value_amplification p95_ms=7 per_req_alloc_bytes=10315458 per_req_allocs=16165
```

control:

```bash
cd poc
make control
```

control output (excerpt):

```
[NC_MARKER]: baggage_single_value_baseline p95_ms=0 per_req_alloc_bytes=133429 per_req_allocs=480
```

**expected:** multiple `baggage` header field-values should be semantically equivalent to a single comma-joined `baggage` value and should not multiply parsing/alloc work within the effective header byte budget.
**actual:** multiple `baggage` header field-values trigger repeated parsing and member aggregation, causing high per-request allocations and increased latency even when each individual value is within 8192 bytes.

## fix recommendation

avoid repeated parsing across multi-values by enforcing a global budget and/or normalizing multi-values into a single value before parsing. one mitigation approach is to treat multi-values as a single comma-joined string and cap total parsed bytes (for example 8192 bytes total).

**fix accepted when:** under the default PoC harness settings, canonical stays within 2x of control for `per_req_alloc_bytes` and `per_req_allocs`, and `p95_ms` stays below 2ms.


[poc.zip](https://github.com/user-attachments/files/25079945/poc.zip)
[PR_DESCRIPTION.md](https://github.com/user-attachments/files/25079946/PR_DESCRIPTION.md)

## References
- https://github.com/open-telemetry/opentelemetry-go/security/advisories/GHSA-mh2q-q3fh-2475
- https://nvd.nist.gov/vuln/detail/CVE-2026-29181
- https://github.com/open-telemetry/opentelemetry-go/pull/7880
- https://github.com/open-telemetry/opentelemetry-go/commit/aa1894e09e3fe66860c7885cb40f98901b35277f
- https://github.com/open-telemetry/opentelemetry-go
- https://github.com/open-telemetry/opentelemetry-go/releases/tag/v1.41.0
