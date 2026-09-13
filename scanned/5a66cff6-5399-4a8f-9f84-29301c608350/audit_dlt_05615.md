# [?] fix: resolve flaky TxPool tests and SpecGasCosts DEBUG crash (#10713)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-04
Source: https://github.com/NethermindEth/nethermind/commit/5f349c98fd52d5a15866582af64f623f5653e555
Type: security-commit

## Details
fix: resolve flaky TxPool tests and SpecGasCosts DEBUG crash (#10713)

* fix and improve flaky tx pool tests

* Fix TxPool test hanging indefinitely on missing TxPoolHeadChanged event (#10715)

* Initial plan

* Use CancellationTokenSource with 5s timeout instead of CancellationToken.None in TxPool test

Co-authored-by: LukaszRozmej <12445221+LukaszRozmej@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: LukaszRozmej <12445221+LukaszRozmej@users.noreply.github.com>

---------

Co-authored-by: Copilot <198982749+Copilot@users.noreply.github.com>
Co-authored-by: LukaszRozmej <12445221+LukaszRozmej@users.noreply.github.com>
