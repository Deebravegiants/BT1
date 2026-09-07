# [?] Fix data race in SyncDurationMetrics timers map (#10277)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-04-24
Source: https://github.com/besu-eth/besu/commit/412dc182ff386ec822d8a012fd3f40bafe731d8e
Type: security-commit

## Details
Fix data race in SyncDurationMetrics timers map (#10277)

* Fix data race in SyncDurationMetrics timers map

Switch the backing map to ConcurrentHashMap; the API surface used
(computeIfAbsent, remove) is unchanged and both operations are atomic.
Metrics-only change, no behavioural impact on sync.

Signed-off-by: Alejandro <26930485+alejandroGM0@users.noreply.github.com>

* Update CHANGELOG.md

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>
Signed-off-by: Alejandro <26930485+alejandroGM0@users.noreply.github.com>

---------

Signed-off-by: Alejandro <26930485+alejandroGM0@users.noreply.github.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>
Co-authored-by: Sally MacFarlane <macfarla.github@gmail.com>
