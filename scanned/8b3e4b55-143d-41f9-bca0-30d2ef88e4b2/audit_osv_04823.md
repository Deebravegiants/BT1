# [H] Envoy Heap Buffer Overflow in TcpStatsdSink

## Summary
Severity: High
Advisory: BIT-envoy-2026-48706
Aliases: CVE-2026-48706, GHSA-7q3f-gwg7-j8g4
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-envoy-2026-48706
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.38.0 <1.38.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. From 1.34.0 until 1.35.13, 1.36.9, 1.37.5, and 1.38.3, a vulnerability exists in Envoy's TCP StatsD sink (TcpStatsdSink), where the thread-local flusher buffer can be overflowed by exceptionally long statistic names (e.g., >16KiB). During formatting, TcpStatsdSink reserves a single contiguous memory slice of 16KiB (FLUSH_SLICE_SIZE_BYTES). If formatting a single metric exceeds the remaining capacity, the flusher initiates a buffer rotation but incorrectly continues to allocate another fixed 16KiB slice. If an attacker can trigger a statistic name longer than 16KiB—for example, by sending an HTTP or gRPC request with an extremely long request path (:path) that is recorded by the grpc_stats filter configured with stats_for_all_methods: true—the flusher will attempt to copy the metric name using memcpy operations beyond the allocated heap buffer boundaries. This leads to a heap write overflow, which can cause immediate denial-of-service (process crash) or potential remote code execution (RCE). This vulnerability is fixed in 1.35.13, 1.36.9, 1.37.5, and 1.38.3.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-7q3f-gwg7-j8g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-48706
