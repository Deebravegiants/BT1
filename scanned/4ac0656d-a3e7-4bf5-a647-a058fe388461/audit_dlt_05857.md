# [?] chore(deps): bump Go vulnerability deps (#21450)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-06-23
Source: https://github.com/ethereum-optimism/optimism/commit/830cf046740898486fab73082c4a9583911db422
Type: security-commit

## Details
chore(deps): bump Go vulnerability deps (#21450)

Bumps Go module dependencies to clear Grype findings on current develop:

- golang.org/x/crypto v0.46.0 -> v0.53.0
- golang.org/x/net v0.48.0 -> v0.56.0
- golang.org/x/sys v0.40.0 -> v0.46.0
- golang.org/x/image v0.25.0 -> v0.43.0
- go.opentelemetry.io/otel{,/trace,/metric} v1.40.0 -> v1.44.0

Related golang.org/x modules updated by the solver: x/mod, x/sync, x/term,
x/text, x/tools, and x/telemetry.

Leaves quic-go/webtransport-go for a separate libp2p upgrade, and leaves the
btcd scanner finding untouched because the latest btcd module split breaks
existing btcutil import paths.
