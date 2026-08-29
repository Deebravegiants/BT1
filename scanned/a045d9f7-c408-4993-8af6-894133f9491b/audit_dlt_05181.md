# [?] Handle quick-xml RUSTSEC-2026-0194/0195: drop unused pprof flamegraph feature, ignore rest

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-02
Source: https://github.com/Conflux-Chain/conflux-rust/commit/4b7cf28dab840a181292f86ba473a7a1a0a0a33a
Type: security-commit

## Details
Handle quick-xml RUSTSEC-2026-0194/0195: drop unused pprof flamegraph feature, ignore rest

quick-xml's DoS fixes ship only in 0.41.0 and no inferno release depends on it yet, so no upgrade path exists today.

pprof's "flamegraph" feature was never used (CPU profiles are served as protobuf only), so dropping it removes the inferno 0.11 -> quick-xml 0.26 subtree outright.

The remaining quick-xml 0.37 comes from jemalloc_pprof's heap-flamegraph SVG endpoint, which only writes SVG and never parses untrusted XML, so the advisories are ignored with justification in deny.toml and .cargo/audit.toml until inferno adopts quick-xml >= 0.41.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
