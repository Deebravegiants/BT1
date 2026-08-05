### Title
Non-recursive deny-filter (`DenyReserveTransferToRelayChain`) misses reserve-asset transfers nested inside `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` - (File: polkadot/xcm/xcm-builder/src/barriers.rs)

### Summary
`DenyReserveTransferToRelayChain::deny_execution` only pattern-matches the top-level instructions of an XCM program and treats `SetAppendix`, `SetErrorHandler`, and `ExecuteWithOrigin` as opaque, always-continue instructions, without inspecting the `Xcm` payload nested inside them. When a runtime composes its barrier as `DenyThenTry<DenyReserveTransferToRelayChain, Allow>` (i.e. without wrapping the deny filter in `DenyRecursively`), a `DepositReserveAsset`/`InitiateReserveWithdraw`/`TransferReserveAsset` targeting `Location { parents: 1, interior: Here }` placed inside a `SetAppendix` (or the other two instructions) bypasses the deny check entirely.

### Finding Description
`DenyReserveTransferToRelayChain::deny_execution` walks the message with `message.matcher().match_next_inst_while(|_| true, |inst| match inst { ... })` [1](#0-0)  — the closure only recognizes `InitiateReserveWithdraw`, `DepositReserveAsset`, `TransferReserveAsset` targeting the relay chain, and `ReserveAssetDeposited`; every other instruction, including `SetAppendix`, `SetErrorHandler`, and `ExecuteWithOrigin`, falls into the catch-all `_ => Ok(ControlFlow::Continue(()))` arm and is skipped without descending into its nested `Xcm` field.

The maintainers explicitly recognized this gap and built `DenyRecursively<Inner>` as the fix: its doc comment states it "checks at the top-level and then **recursively**" and "this barrier only applies to **locally executed** XCM instructions (`SetAppendix`, `SetErrorHandler`, and `ExecuteWithOrigin`)" [2](#0-1) . Its `deny_execution` implementation first runs `Inner::deny_execution` on the top level, then explicitly matches `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` and recurses into their nested XCM with `Self::deny_recursively` [3](#0-2) . This confirms that the bare `DenyReserveTransferToRelayChain` (and any other `DenyExecution` impl not wrapped in `DenyRecursively`) is, by construction, a single-level scan that cannot see instructions embedded inside `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin`.

Exploit flow for a runtime whose `Barrier` type is configured as `DenyThenTry<DenyReserveTransferToRelayChain, Allow>` (i.e., omitting `DenyRecursively`):
1. An unprivileged parachain account submits (via `pallet_xcm::execute` or via HRMP/XCMP from another chain it controls) the XCM program `Xcm([SetAppendix(Xcm([DepositReserveAsset { dest: Location { parents: 1, interior: Here }, .. }]))])`.
2. The barrier's `DenyReserveTransferToRelayChain::deny_execution` scans the top-level instruction `SetAppendix(..)`, which does not match any of the deny arms, so it returns `Ok(ControlFlow::Continue(()))` and never inspects the nested `Xcm`.
3. `Allow` (e.g. `AllowTopLevelPaidExecutionFrom`/`WithComputedOrigin` combos) is then evaluated against the top level and, if it accepts (e.g., the message is preceded by an asset deposit + `BuyExecution`), the message passes the barrier.
4. The XCM executor then actually executes `SetAppendix`, and when the main program errors or completes, the appendix executes `DepositReserveAsset` targeting the relay chain — the exact operation governance intended to forbid.

### Impact Explanation
For any runtime whose barrier stack uses `DenyReserveTransferToRelayChain` without the `DenyRecursively` wrapper, an unprivileged XCM sender can perform reserve-asset transfers to the relay chain that the deny-filter was meant to block, by hiding the transfer instruction inside `SetAppendix`, `SetErrorHandler`, or `ExecuteWithOrigin`. This is exactly the scoped impact: unauthorized reserve-asset transfer to the relay chain circumventing a governance-mandated deny rule (see the original motivating issue referenced in the code, paritytech/polkadot#5233) [4](#0-3) .

### Likelihood Explanation
The vulnerability is fully deterministic in the `xcm-builder` primitive itself: any barrier composition that uses `DenyReserveTransferToRelayChain` (or another `DenyExecution` impl) without `DenyRecursively` is bypassable this way, with no special privileges, race conditions, or timing needed — just crafting the XCM message with the deny-triggering instruction nested one level inside `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin`. I could not fully confirm from the indexed snippets which shipped production runtimes (asset-hub, bridge-hub, etc.) currently wrap their deny filter in `DenyRecursively` versus using the bare filter, since the index only returned match counts, not the resolved `Barrier` type definitions, for those files — this should be verified directly in each runtime's `xcm_config.rs` (specifically the `type Barrier = ...` definition) before treating any specific production chain as impacted. The bug is real and concrete at the `xcm-builder` primitive level, and is conditional exactly as the question frames it: it only manifests for runtimes/config choices that don't opt into `DenyRecursively`.

### Recommendation
- All production runtime `Barrier` definitions using `DenyReserveTransferToRelayChain` (or any other deny-filter meant to enforce a security-relevant restriction) should wrap it in `DenyRecursively`, i.e. use `DenyThenTry<DenyRecursively<DenyReserveTransferToRelayChain>, Allow>` rather than `DenyThenTry<DenyReserveTransferToRelayChain, Allow>`.
- Consider hard-deprecating or renaming the non-recursive `DenyExecution` composition path in `DenyThenTry` (or adding a lint/compile-time warning) so that plain deny-filters can't accidentally be used as the sole line of defense without recursion, given that `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` are known local-execution vectors.
- Audit all downstream runtimes (asset-hub-*, bridge-hub-*, collectives-*, coretime-*, people-*, template parachain, staking-async parachain) to confirm their `Barrier` type wraps `DenyReserveTransferToRelayChain` in `DenyRecursively`.

### Proof of Concept
Add a unit test in `polkadot/xcm/xcm-builder/src/tests/barriers.rs` mirroring the existing `deny_recursively_then_try_works` test, but comparing the two compositions directly:
```rust
#[test]
fn deny_reserve_transfer_bypassed_without_deny_recursively() {
    let dest_relay = Location { parents: 1, interior: Here };
    let mut nested_deny_msg = Xcm::<()>(vec![
        SetAppendix(Xcm(vec![DepositReserveAsset {
            assets: All.into(),
            dest: dest_relay.clone(),
            xcm: Xcm(vec![]),
        }])),
    ]);

    // Non-recursive: should be Ok (bypassed) — proving the bug.
    let mut msg = nested_deny_msg.clone();
    assert!(DenyReserveTransferToRelayChain::deny_execution(
        &Location::parent(), msg.inner_mut(), Weight::MAX, &mut Properties { weight_credit: Weight::MAX, message_id: None }
    ).is_ok());

    // Recursive: should be Err(Unsupported) — the fix.
    let mut msg2 = nested_deny_msg;
    assert_eq!(
        DenyRecursively::<DenyReserveTransferToRelayChain>::deny_execution(
            &Location::parent(), msg2.inner_mut(), Weight::MAX, &mut Properties { weight_credit: Weight::MAX, message_id: None }
        ),
        Err(ProcessMessageError::Unsupported)
    );
}
```
Expected assertions: the first call passes (`Ok(())`) demonstrating the top-level scan misses the nested `DepositReserveAsset`, while the second call with `DenyRecursively` correctly rejects the message with `ProcessMessageError::Unsupported`, proving the gap and the fix.

### Citations

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L553-554)
```rust
// See issue <https://github.com/paritytech/polkadot/issues/5233>
pub struct DenyReserveTransferToRelayChain;
```

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L562-588)
```rust
		message.matcher().match_next_inst_while(
			|_| true,
			|inst| match inst {
				InitiateReserveWithdraw {
					reserve: Location { parents: 1, interior: Here },
					..
				} |
				DepositReserveAsset { dest: Location { parents: 1, interior: Here }, .. } |
				TransferReserveAsset { dest: Location { parents: 1, interior: Here }, .. } => {
					Err(ProcessMessageError::Unsupported) // Deny
				},

				// An unexpected reserve transfer has arrived from the Relay Chain. Generally,
				// `IsReserve` should not allow this, but we just log it here.
				ReserveAssetDeposited { .. }
					if matches!(origin, Location { parents: 1, interior: Here }) =>
				{
					tracing::debug!(
						target: "xcm::barriers",
						"Unexpected ReserveAssetDeposited from the Relay Chain",
					);
					Ok(ControlFlow::Continue(()))
				},

				_ => Ok(ControlFlow::Continue(())),
			},
		)?;
```

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L595-604)
```rust
/// Denies execution if the XCM contains instructions not meant to run on this chain,
/// first checking at the top-level and then **recursively**.
///
/// This barrier only applies to **locally executed** XCM instructions (`SetAppendix`,
/// `SetErrorHandler`, and `ExecuteWithOrigin`). Remote parts of the XCM are expected to be
/// validated by the receiving chain's barrier.
///
/// Note: Ensures that restricted instructions do not execute on the local chain, enforcing stricter
/// execution policies while allowing remote chains to enforce their own rules.
pub struct DenyRecursively<Inner>(PhantomData<Inner>);
```

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L653-679)
```rust
	fn deny_execution<RuntimeCall>(
		origin: &Location,
		instructions: &mut [Instruction<RuntimeCall>],
		max_weight: Weight,
		properties: &mut Properties,
	) -> Result<(), ProcessMessageError> {
		// First, check if the top-level message should be denied.
		Inner::deny_execution(origin, instructions, max_weight, properties).inspect_err(|e| {
			tracing::debug!(
				target: "xcm::barriers",
				"DenyRecursively::Inner denied execution, origin: {:?}, instructions: {:?}, max_weight: {:?}, properties: {:?}, error: {:?}",
				origin, instructions, max_weight, properties, e
			);
		})?;

		// If the top-level check passes, check nested instructions recursively.
		instructions.matcher().match_next_inst_while(
			|_| true,
			|inst| match inst {
				SetAppendix(nested_xcm) |
				SetErrorHandler(nested_xcm) |
				ExecuteWithOrigin { xcm: nested_xcm, .. } => Self::deny_recursively::<RuntimeCall>(
					origin, nested_xcm, max_weight, properties,
				),
				_ => Ok(ControlFlow::Continue(())),
			},
		)?;
```
