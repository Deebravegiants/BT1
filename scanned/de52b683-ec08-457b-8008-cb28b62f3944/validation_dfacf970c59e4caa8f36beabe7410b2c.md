### Title
`DenyReserveTransferToRelayChain` does not match the `InitiateTransfer` instruction, allowing relay-chain reserve transfers to bypass the deny filter - ([File: polkadot/xcm/xcm-builder/src/barriers.rs])

### Summary
`DenyReserveTransferToRelayChain::deny_execution` only pattern-matches `InitiateReserveWithdraw`, `DepositReserveAsset`, and `TransferReserveAsset` with a relay-chain destination (`parents: 1, interior: Here`). It does not match the newer `InitiateTransfer` instruction (XCM v5), which consolidates the same reserve-transfer/teleport semantics into a single instruction with a `destination` field. An unprivileged user can therefore construct a top-level (or `DenyRecursively`-nested) XCM using `InitiateTransfer { destination: (1, Here), .. }` to move assets to the Relay Chain sovereign account without tripping the deny filter that was specifically designed to block this class of transfer (see issue referenced in the code: `paritytech/polkadot#5233`).

### Finding Description
`DenyReserveTransferToRelayChain::deny_execution` in `polkadot/xcm/xcm-builder/src/barriers.rs` (lines 555–591) walks the instruction slice and matches specific legacy instruction variants:
```rust
InitiateReserveWithdraw { reserve: Location { parents: 1, interior: Here }, .. } |
DepositReserveAsset { dest: Location { parents: 1, interior: Here }, .. } |
TransferReserveAsset { dest: Location { parents: 1, interior: Here }, .. } => {
    Err(ProcessMessageError::Unsupported) // Deny
},
_ => Ok(ControlFlow::Continue(())),
```
`InitiateTransfer` is not one of the matched arms, so it falls into the `_ => Ok(ControlFlow::Continue(()))` catch-all and is silently allowed to pass. `InitiateTransfer` was introduced to consolidate `DepositReserveAsset`/`InitiateReserveWithdraw`/teleport-style transfers into one instruction with a `destination` field, and the executor (`polkadot/xcm/xcm-executor/src/lib.rs`) processes it as a first-class, locally-executed instruction that withdraws/burns local assets and forwards a message to `destination`.

`DenyRecursively` (lines 604–684) only descends into `SetAppendix`, `SetErrorHandler`, and `ExecuteWithOrigin` nested programs and re-applies the `Inner` deny filter (here, `DenyReserveTransferToRelayChain`) at each nesting level. Because the `Inner` filter itself has no arm for `InitiateTransfer`, no amount of correct recursive traversal by `DenyRecursively` will catch it — the instruction is invisible to the filter both at the top level and at every nested level. This is a gap in the `Inner` matcher, not a traversal gap in `DenyRecursively`, but the net effect is that `DenyThenTry<DenyRecursively<DenyReserveTransferToRelayChain>, ..>` fails to block a semantically equivalent reserve-transfer-to-relay-chain operation.

An unprivileged user with access to any XCM execution entry point that accepts user-authored programs (e.g. `pallet_xcm::execute`, or `Transact`/`ExecuteWithOrigin`-wrapped sub-programs, or a locally-originated program subject to this barrier) can submit:
```
WithdrawAsset(...)
InitiateTransfer { destination: (1, Here).into(), assets: ..., remote_xcm: Xcm(vec![]), .. }
```
This passes `DenyReserveTransferToRelayChain` unmodified and executes normally in the XCM executor, resulting in the same relay-chain-sovereign-account deposit that `TransferReserveAsset`/`DepositReserveAsset` to `(1, Here)` would have produced and that the barrier was designed to prevent.

### Impact Explanation
This bypasses a deliberate security control (tracked against `paritytech/polkadot#5233`) intended to prevent chains from allowing users to reserve-transfer assets directly to the Relay Chain (which can have unintended reserve/backing implications for the Relay Chain's own asset accounting). Assets can be moved to the Relay Chain sovereign account via a code path the runtime configuration explicitly tried to close off, undermining the chain operator's intended reserve-transfer policy. It does not, by itself, allow theft of others' assets or duplication, since the sender must own/withdraw the assets — but it does defeat an explicit deny-list security control on any chain relying on `DenyReserveTransferToRelayChain` to block this exact behavior once `InitiateTransfer` is available/enabled in the executor's instruction set.

### Likelihood Explanation
High feasibility on any runtime that (a) includes `DenyThenTry<DenyRecursively<DenyReserveTransferToRelayChain>, ..>` (or `DenyReserveTransferToRelayChain` directly) in its `Barrier`, and (b) permits XCM v5-encoded programs containing `InitiateTransfer` to reach `should_execute`/`deny_execution` — which is standard for chains that have upgraded to support XCM v5. No special privileges, proxies, or governance are needed; a normal user submitting a self-authored XCM via `pallet_xcm::execute` (or any accepted program path) can trigger it repeatably.

### Recommendation
Add an `InitiateTransfer { destination: Location { parents: 1, interior: Here }, .. }` arm to `DenyReserveTransferToRelayChain::deny_execution` (and any other deny filters intended to be instruction-set-agnostic) so it is rejected identically to `TransferReserveAsset`/`DepositReserveAsset`/`InitiateReserveWithdraw`. More generally, audit all `DenyExecution` implementations for coverage of every XCM instruction variant that can effect a "send assets away" pattern across all currently supported XCM versions, and add a compile-time/test-time exhaustiveness check (e.g., a match with no wildcard fallback, or a dedicated unit test enumerating all instruction variants) to prevent silent gaps when new instructions are added.

### Proof of Concept
Rust unit test in `polkadot/xcm/xcm-builder/src/tests/barriers.rs` style:
```rust
#[test]
fn deny_reserve_transfer_to_relay_chain_blocks_initiate_transfer() {
    let mut message = Xcm(vec![
        WithdrawAsset((Here, 100u128).into()),
        InitiateTransfer {
            destination: Location::parent(),
            remote_fees: None,
            preserve_origin: false,
            assets: vec![AssetTransferFilter::ReserveDeposit(All)],
            remote_xcm: Xcm(vec![]),
        },
    ]);
    let mut properties = Properties { weight_credit: Weight::zero(), message_id: None };
    let origin = Location::new(0, [AccountId32 { id: [0u8;32], network: None }]);

    // Expect this to be denied just like TransferReserveAsset/DepositReserveAsset to (1, Here),
    // but currently it is NOT denied.
    let result = DenyThenTry::<DenyRecursively<DenyReserveTransferToRelayChain>, AllowUnpaidExecutionFrom<Everything>>
        ::should_execute(&origin, &mut message.0, Weight::from_parts(100, 100), &mut properties);

    assert_eq!(result, Err(ProcessMessageError::Unsupported)); // currently fails: result is Ok(())
}
```
Expected: with the current code, the assertion fails because `should_execute` returns `Ok(())`, proving `InitiateTransfer` to `(1, Here)` is not denied. A fuzz/invariant extension can additionally generate random nesting via `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` wrapping `InitiateTransfer { destination: (1, Here) }` at varying depths and assert `DenyThenTry::should_execute` always returns `Err(ProcessMessageError::Unsupported)`; all such cases will currently pass through undetected, confirming the gap exists both at top level and at every recursion depth.