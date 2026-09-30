# [M] RustFS gRPC GetMetrics deserialization panic enables remote DoS

## Summary
Severity: Medium
Advisory: GHSA-gw2x-q739-qhcr
CVE: CVE-2025-69255
CWE: CWE-755
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-gw2x-q739-qhcr
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=1.0.0-alpha.13 <1.0.0-alpha.78

## Details
### Summary
A malformed gRPC `GetMetrics` request causes `get_metrics` to `unwrap()` failed deserialization of `metric_type`/`opts`, panicking the handler thread and enabling remote denial of service of the metrics endpoint.

### Details
- Vulnerable code: `rustfs/src/storage/tonic_service.rs:1775-1782`:
  - `MetricType` and `CollectMetricsOpts` are deserialized with `Deserialize::deserialize(...).unwrap()` from client-supplied bytes.
  - Malformed `metric_type`/`opts` (e.g., empty or truncated rmp-serde payloads) trigger `InvalidMarkerRead` and panic.
- Reachability: same TCP listener as S3 (default `:9000`); only a static interceptor token `authorization: rustfs rpc` is checked in `server/http.rs:677`.
- Impact scope: panic terminates the worker handling the request, causing metrics service interruption and potential process instability.

### PoC

[rustfs-grpc-metrics-invalid-metric-type-panic-poc.tar.gz](https://github.com/user-attachments/files/24038341/rustfs-grpc-metrics-invalid-metric-type-panic-poc.tar.gz)


1) Start RustFS (example local dev):
```bash
mkdir -p /tmp/rustfs-data1 /tmp/rustfs-data2
RUSTFS_ACCESS_KEY=devadmin RUSTFS_SECRET_KEY=devadmin \
  cargo run --bin rustfs -- --address 0.0.0.0:9000 \
  /tmp/rustfs-data1 /tmp/rustfs-data2
```
2) From `rustfs-grpc-metrics-invalid-metric-type-panic-poc/`, run:
```bash
ENDPOINT=127.0.0.1:9000 make run
# or: grpcurl -plaintext \
#   -H 'authorization: rustfs rpc' \
#   -import-path ../crates/protos/src -proto node.proto \
#   -d '{"metric_type":"","opts":""}' \
#   127.0.0.1:9000 node_service.NodeService/GetMetrics
```
3) Observe panic in server logs at `tonic_service.rs:get_metrics` with `InvalidMarkerRead` and worker crash; client output saved to `poc-response.txt`/`poc-grpcurl.log`.

### Impact
- Vulnerability type: remote unauthenticated (static token) denial of service via panic in gRPC handler.
- Who is impacted: any deployment exposing the gRPC endpoint where an attacker can reach port 9000 and supply the known `authorization: rustfs rpc` header; metrics service is disrupted and may affect overall stability depending on runtime crash handling.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-gw2x-q739-qhcr
- https://nvd.nist.gov/vuln/detail/CVE-2025-69255
- https://github.com/rustfs/rustfs/commit/eb33e82b56ed11fd12bb39416359d8d60737dc7a
- https://github.com/rustfs/rustfs
