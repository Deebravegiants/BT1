# [?] Fix WASM block producer panic (#11206)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2022-04-13
Source: https://github.com/paritytech/substrate/commit/32510e13afa84a2fa917a94e5d7e18d480a34a22
Type: security-commit

## Details
Fix WASM block producer panic (#11206)

* Box events

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Fix tests

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Revert "Box events"

This reverts commit 9fb1887cd23eb272844d63640b0b2d9ba3e549a1.

* Revert "Fix tests"

This reverts commit 981c50f23a7c514c9527299734bc6bc5b77a817f.

* Use simpler approach

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>

* Update doc

Signed-off-by: Oliver Tale-Yazdi <oliver.tale-yazdi@parity.io>
