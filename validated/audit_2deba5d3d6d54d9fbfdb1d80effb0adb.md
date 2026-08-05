Audit Report

## Title
`DenyReserveTransferToRelayChain` can be bypassed via reserve-transfer instructions nested inside `SetAppendix`/`SetErrorHandler` sub-programs - (File: polkadot/xcm/xcm-builder/src/barriers.rs)

## Summary
`DenyReserveTransferToRelayChain::deny_execution` walks only the flat, top-level instruction slice via `Matcher::match_next_inst_while`, with a wildcard arm that simply continues past any instruction it doesn't recognize, including `SetAppendix`/`SetErrorHandler`. Because these instructions carry a nested `Xcm<Call>` payload that is never inspected, a `DepositReserveAsset`/`InitiateReserveWithdraw`/`TransferReserveAsset` targeting the relay chain hidden inside a `SetErrorHandler` (triggered later by a `Trap`) or `SetAppendix` sub-program is never subject to the deny check, even though it is executed by the same XCM VM instance with full access to the Holding register.

## Finding Description
`DenyReserveTransferToRelayChain::deny_execution` in `polkadot/xcm/xcm-builder/src/barriers.rs` matches only top-level enum variants: [1](#0-0) 

The wildcard arm `_ => Ok(ControlFlow::Continue(()))` means `SetAppendix(nested_xcm)` and `SetErrorHandler(nested_xcm)` fall through untouched — the nested `Xcm<Call>` payload is never scanned for embedded reserve-transfer instructions. `Matcher::match_next_inst_while` (as cited in the original report from `polkadot/xcm/xcm-builder/src/matcher.rs`) only iterates over the flat slice it was given, confirming there is no descent into nested instructions in this specific implementation.

Notably, the codebase already contains a purpose-built mitigation for exactly this class of issue: `DenyRecursively<Inner>`, which explicitly recurses into `SetAppendix`, `SetErrorHandler`, and `ExecuteWithOrigin` nested XCMs with a bounded recursion counter: [2](#0-1) 

This confirms the maintainers recognize that a bare `Deny*` barrier operating only on the top-level slice is insufficient against nested `SetAppendix`/`SetErrorHandler` payloads — that is the whole reason `DenyRecursively` was introduced.

However, `DenyRecursively` is not universally applied. Grepping runtime configs shows that only `cumulus/parachains/runtimes/bridge-hubs/bridge-hub-westend/src/xcm_config.rs` and `templates/parachain/runtime/src/configs/xcm_config.rs` reference `DenyRecursively`, while `asset-hub-rococo`, `asset-hub-westend`, `bridge-hub-rococo`, `collectives-westend`, `coretime-westend`, `people-westend`, `yet-another-parachain`, and the `staking-async` parachain template configs reference only the bare `DenyReserveTransferToRelayChain`/`DenyThenTry` combination without the recursive wrapper.

## Impact Explanation
On any parachain runtime that composes `DenyThenTry<DenyReserveTransferToRelayChain, Allow...>` without wrapping the deny-side in `DenyRecursively`, a user can bypass the explicit policy restriction against sending reserve-backed assets to the relay chain by embedding the `DepositReserveAsset`/`InitiateReserveWithdraw`/`TransferReserveAsset` instruction inside a `SetErrorHandler` (triggered via `Trap`) or `SetAppendix` sub-program. This defeats a security control intended to prevent asset-hub-style accounting/backing violations from reserve transfers to the relay chain's sovereign account.

## Likelihood Explanation
The exploit only requires a signed account with access to `pallet_xcm::execute` (or any origin accepted by the chain's `Allow` barrier), no privileged origin or race condition, and is fully deterministic: `WithdrawAsset -> ClearOrigin -> BuyExecution -> SetErrorHandler(DepositReserveAsset{dest: Parent, ..}) -> Trap(0)` passes `DenyReserveTransferToRelayChain`'s top-level scan (since `SetErrorHandler` is unmatched at the top level) and the subsequent `Allow` barrier, then executes the reserve transfer to the relay chain when the appendix/error-handler runs.

## Recommendation
Wrap `DenyReserveTransferToRelayChain` (and any other `Deny*` barrier relying on `match_next_inst_while` over only the top-level slice) in the existing `DenyRecursively` combinator across all runtime configurations that use it, so that nested `Xcm` payloads inside `SetAppendix`/`SetErrorHandler`/`ExecuteWithOrigin` are checked at any nesting depth — consistent with what has already been done for `bridge-hub-westend` and the parachain template.

## Proof of Concept
Unit test in `polkadot/xcm/xcm-builder/src/tests/barriers.rs` invoking `DenyReserveTransferToRelayChain::should_execute` (or `deny_execution`) directly on:
```rust
Xcm(vec![
    WithdrawAsset((Here, 100u128).into()),
    ClearOrigin,
    SetErrorHandler(Xcm(vec![DepositReserveAsset {
        assets: Wild(All),
        dest: Parent.into(),
        xcm: Xcm(vec![]),
    }])),
    Trap(0),
])
```
This currently returns `Ok(())` from `DenyReserveTransferToRelayChain`, demonstrating the bypass on any runtime that does not wrap it in `DenyRecursively`; it should return `Err(ProcessMessageError::Unsupported)` once the barrier is composed with `DenyRecursively` as recommended.

### Citations

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L554-591)
```rust
pub struct DenyReserveTransferToRelayChain;
impl DenyExecution for DenyReserveTransferToRelayChain {
	fn deny_execution<RuntimeCall>(
		origin: &Location,
		message: &mut [Instruction<RuntimeCall>],
		_max_weight: Weight,
		_properties: &mut Properties,
	) -> Result<(), ProcessMessageError> {
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
		Ok(())
	}
}
```

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L593-684)
```rust
environmental::environmental!(recursion_count: u8);

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

impl<Inner: DenyExecution> DenyRecursively<Inner> {
	/// Recursively applies the deny filter to a nested XCM.
	///
	/// Ensures that restricted instructions are blocked at any depth within the XCM.
	/// Uses a **recursion counter** to prevent stack overflows from deep nesting.
	fn deny_recursively<RuntimeCall>(
		origin: &Location,
		xcm: &mut Xcm<RuntimeCall>,
		max_weight: Weight,
		properties: &mut Properties,
	) -> Result<ControlFlow<()>, ProcessMessageError> {
		// Initialise recursion counter for this execution context.
		recursion_count::using_once(&mut 1, || {
			// Prevent stack overflow by enforcing a recursion depth limit.
			recursion_count::with(|count| {
				if *count > xcm_executor::RECURSION_LIMIT {
					tracing::debug!(
                    	target: "xcm::barriers",
                    	"Recursion limit exceeded (count: {count}), origin: {:?}, xcm: {:?}, max_weight: {:?}, properties: {:?}",
                    	origin, xcm, max_weight, properties
                	);
					return None;
				}
				*count = count.saturating_add(1);
				Some(())
			}).flatten().ok_or(ProcessMessageError::StackLimitReached)?;

			// Ensure the counter is decremented even if an early return occurs.
			sp_core::defer! {
				recursion_count::with(|count| {
					*count = count.saturating_sub(1);
				});
			}

			// Recursively check the nested XCM instructions.
			Self::deny_execution(origin, xcm.inner_mut(), max_weight, properties)
		})?;

		Ok(ControlFlow::Continue(()))
	}
}

impl<Inner: DenyExecution> DenyExecution for DenyRecursively<Inner> {
	/// Denies execution of restricted local nested XCM instructions.
	///
	/// This checks for `SetAppendix`, `SetErrorHandler`, and `ExecuteWithOrigin` instruction
	/// applying the deny filter **recursively** to any nested XCMs found.
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

		// Permit everything else
		Ok(())
	}
}
```
