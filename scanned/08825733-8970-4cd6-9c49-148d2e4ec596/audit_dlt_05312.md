# [?] Fix flaky TestFollowerHappyPath panic on pebble DB close

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-02-25
Source: https://github.com/onflow/flow-go/commit/a5199f4cdf156db3864a30083f2c411ef027e024
Type: security-commit

## Details
Fix flaky TestFollowerHappyPath panic on pebble DB close

Increase teardown AllDone timeout from 1s to 10s to give the engine
enough time to drain queued work after cancellation.

Co-Authored-By: Claude Sonnet 4.6 (1M context) <noreply@anthropic.com>
