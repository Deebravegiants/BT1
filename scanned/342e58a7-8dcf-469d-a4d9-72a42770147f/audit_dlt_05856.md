# [?] Fix nil pointer dereference when version alerter skips and reset test state

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-18
Source: https://github.com/OffchainLabs/nitro/commit/f63dc07b19d4ffef16171e05a34d40b37244a254
Type: security-commit

## Details
Fix nil pointer dereference when version alerter skips and reset test state

Guard against nil alerter in cmd/nitro when NewClient returns (nil, nil)
for invalid semver versions. Also explicitly reset UpgradeGracePeriod
before the ERROR test phase to avoid implicit state carry-over from the
WARN phase.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
