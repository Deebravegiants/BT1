# [M] opentelemetry-go's baggage parsing no longer caps raw header length

## Summary
Severity: Medium
Advisory: GHSA-5wrp-cwcj-q835
CVE: CVE-2026-41178
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-5wrp-cwcj-q835
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/otel/baggage` — affected >=1.41.0 <1.42.0
- Go: `go.opentelemetry.io/otel/propagation` — affected >=1.41.0 <1.42.0
- Go: `go.opentelemetry.io/otel/baggage` — affected >=1.43.0 <1.44.0
- Go: `go.opentelemetry.io/otel/propagation` — affected >=1.43.0 <1.44.0

## Details
### Summary

https://github.com/open-telemetry/opentelemetry-go/pull/7880 removed raw-length rejection and it causes `Parse` to process arbitrarily large/invalid baggage headers and log errors, enabling DoS via oversized inputs.


### Details

The commit removes the upfront baggage-string length check and the per-member size guard in parsing. `Parse` now walks the entire input with `strings.SplitSeq` and skips invalid members while continuing to process the rest. For very large or malformed `baggage` headers, the parser still fully tokenizes and percent-decodes each member, and errors are forwarded to the global error handler (default logging). This lets a remote client send oversized/invalid headers to trigger excessive CPU/memory work and potentially large log output before any size limit is enforced, creating a denial-of-service risk in services that do not already enforce strict header size limits.

Summary:
- In `baggage/baggage.go`, `parseMember` performs full parsing and `PathUnescape` on the entire member without any size guard, amplifying work for large inputs. `Parse` no longer checks bStr length and continues processing invalid members, so oversized/invalid headers are fully parsed instead of being rejected early.
- In `propagation/baggage.go`, parsing errors from attacker-controlled headers are sent to the global error handler (default logging), which can amplify oversized-input impact.

### PoC

[baggage_dos_poc.tar.gz](https://github.com/user-attachments/files/26677819/baggage_dos_poc.tar.gz)

### Impact

The issue is reachable through standard propagation parsing (in-scope) and can be exploited remotely to cause CPU/log amplification, but the impact is availability-only and bounded by transport header limits and configurable error handling, supporting a medium severity rather than high/critical.

`baggage.Parse` iterates over all list members with `strings.SplitSeq` and skips invalid members while continuing, without a raw-length guard. `parseMember` performs full parsing and `PathUnescape` on each member, and `propagation.Baggage` forwards parsing errors to the global error handler, which logs by default. A remote client can therefore send oversized/invalid baggage headers that bypass the 8KB limit for valid members, causing extra CPU work and large log output, resulting in availability/log amplification in services that accept large headers and use the default handler.

Assumptions:

- An instrumented service uses the OpenTelemetry baggage propagator for inbound request parsing.
- Attackers can send oversized or malformed baggage headers that pass the hosting server/proxy header size limits.
- The default error handler is used or logs are otherwise emitted for parse errors.
- Inbound request parsing with propagation.Baggage
- Oversized/invalid baggage headers accepted by the HTTP/gRPC stack
- Error handler not suppressing parse errors

## References
- https://github.com/open-telemetry/opentelemetry-go/security/advisories/GHSA-5wrp-cwcj-q835
- https://nvd.nist.gov/vuln/detail/CVE-2026-41178
- https://github.com/open-telemetry/opentelemetry-go/pull/7880
- https://github.com/open-telemetry/opentelemetry-go
