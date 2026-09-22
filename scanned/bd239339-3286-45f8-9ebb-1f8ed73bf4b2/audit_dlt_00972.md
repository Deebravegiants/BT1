# [?] fix(metrics): disable otel exemplars to prevent rune overflow (#11211)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2026-02-25
Source: https://github.com/ipfs/kubo/commit/f55bbdd539cb50c80ad7ecc1c68bd9c10340a8b7
Type: security-commit

## Details
fix(metrics): disable otel exemplars to prevent rune overflow (#11211)

* fix: disable otel exemplars to prevent prometheus rune overflow

the OTel SDK View from #11208 drops server.address from http.server.*
metric labels, but the OTel spec requires filtered attributes to be
carried as exemplar FilteredAttributes. on subdomain gateways the
server.address value (e.g. "CID.ipfs.dweb.link") combined with
trace_id and span_id exceeds the 128-rune prometheus exemplar limit.

- cmd/ipfs/kubo/daemon.go: add exemplar.AlwaysOffFilter to MeterProvider
- docs/changelogs/v0.40.md: document exemplar disable in metrics section

(cherry picked from commit 221741ee20581a0968b3989adab4e44fbcf9a527)
