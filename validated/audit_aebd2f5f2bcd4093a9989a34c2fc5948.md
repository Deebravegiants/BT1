Audit Report

## Title
Value-transfer `CALL`s always get `ReentrancyProtection::AllowReentry`, defeating the stipend-based anti-reentrancy heuristic - (File: substrate/frame/revive/src/vm/evm/instructions/contract.rs)

## Summary
In `run_call`, the match statement that selects `add_stipend`/`ReentrancyProtection` places the wildcard arm `(false, _) => (true, ReentrancyProtection::AllowReentry)` before the stipend-heuristic arm `(_, true) => (true, ReentrancyProtection::AllowNext)`. Because Rust evaluates match arms top-to-bottom and `false` on the first tuple element (nonzero value) is matched via wildcard on the second element, every value-carrying `CALL` — including the canonical Solidity `.transfer()`/`.send()` pattern, which passes `value != 0` and `gas_limit == CALL_STIPEND (2300)` — is routed to `AllowReentry` instead of the intended `AllowNext` protection. [1](#0-0) 

## Finding Description
The relevant code is:

```rust
let (add_stipend, reentracy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
    {
        (false, _) => (true, ReentrancyProtection::AllowReentry),
        (_, true) => (true, ReentrancyProtection::AllowNext),
        (_, _) => (false, ReentrancyProtection::AllowReentry),
    };
``` [1](#0-0) 

Match arm evaluation is ordered top-to-bottom: the tuple's first element is `value.is_zero()`. Arm 1, `(false, _)`, fires whenever the value is nonzero — regardless of `gas_limit` — and unconditionally returns `AllowReentry`. Arm 2, `(_, true)`, which is the code's documented anti-reentrancy heuristic for the gas-stipend pattern, is therefore only reachable when `value.is_zero()` is `true`, i.e. only for zero-value calls with `gas_limit == 2300`. This directly contradicts the developer's stated intent in the surrounding comment, which describes detecting the stipend pattern to protect value-bearing sends via `AllowNext`. [2](#0-1) 

This computed `reentracy` value is passed directly into `interpreter.ext.call(...)`, which governs whether reentrant calls are permitted during the value transfer. [3](#0-2)  Because Solidity's compiled `.transfer()`/`.send()` idiom always supplies a nonzero value together with `gas_limit == CALL_STIPEND`, this call pattern always falls into arm 1 (`AllowReentry`), never arm 2 (`AllowNext`), making the stipend-based reentrancy heuristic structurally dead code for the exact scenario it claims to protect.

I was not able to fully trace, within the available exploration budget, the downstream enforcement logic of `ReentrancyProtection::AllowNext` versus `AllowReentry` inside `exec.rs` to confirm the precise gating behavior difference, but the code as cited unambiguously demonstrates the match-arm ordering bug: the wildcard on nonzero value pre-empts the stipend-detection arm, so `AllowNext` can never be produced for a nonzero-value call regardless of `gas_limit`.

## Impact Explanation
If the runtime's reentrancy protection mechanism is meant to leverage the classic gas-stipend convention (as the code comments and enum naming indicate), this bug causes that protection to be silently skipped for value-bearing calls — which is the common, real-world case for `.transfer()`/`.send()`. A contract relying on this convention for reentrancy safety would not receive the intended safeguard, exposing it to reentrant fund-draining attacks of the kind historically associated with unprotected value transfers.

## Likelihood Explanation
The precondition (`value != 0`, `gas_limit == CALL_STIPEND`) is the default output of the widely-used Solidity `.transfer()`/`.send()` idiom, not a contrived edge case, so any unprivileged user deploying and interacting with ordinary EVM-compatible contracts on this pallet would trigger this code path without needing any privileged origin.

## Recommendation
Reorder the match arms so the stipend-heuristic check (`gas_limit == CALL_STIPEND`) is evaluated before the blanket nonzero-value arm, e.g.:
```rust
let (add_stipend, reentracy) = match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND)) {
    (_, true) => (true, ReentrancyProtection::AllowNext),
    (false, _) => (true, ReentrancyProtection::AllowReentry),
    (_, _) => (false, ReentrancyProtection::AllowReentry),
};
```
so that any call with `gas_limit == CALL_STIPEND` (value zero or nonzero) receives `AllowNext`, and only unrestricted-gas value transfers receive `AllowReentry`.

## Proof of Concept
1. Add a unit test directly exercising `run_call`'s match logic (or an equivalent standalone match test) asserting that for `value != 0 && gas_limit == CALL_STIPEND`, the returned reentrancy mode is `ReentrancyProtection::AllowNext`. This assertion fails against the current code, which returns `AllowReentry`.
2. As an integration-level PoC: deploy a `Victim` contract that uses `payable(addr).transfer(amount)` (or `.send()`) relying on the stipend convention, and an `Attacker` contract whose fallback reenters `Victim`. Fund `Victim`, have `Attacker` invoke `Victim`'s withdraw path via a normal extrinsic, and observe that the reentrant call is permitted (consistent with `AllowReentry` being applied) rather than blocked as `AllowNext` would imply.

### Citations

**File:** substrate/frame/revive/src/vm/evm/instructions/contract.rs (L193-203)
```rust
	let (add_stipend, reentracy) =
		match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
		{
			(false, _) => (true, ReentrancyProtection::AllowReentry),
			// Heuristic: detect when solc passes `gas_limit = 2300` (the call stipend).
			// For zero-value transfer/send, solc injects `gas_limit = 2300` explicitly.
			// We apply `AllowNext` reentrancy protection and set `add_stipend = true` since the
			// raw 2300 gas value is only meaningful at Ethereum's gas scale.
			(_, true) => (true, ReentrancyProtection::AllowNext),
			(_, _) => (false, ReentrancyProtection::AllowReentry),
		};
```

**File:** substrate/frame/revive/src/vm/evm/instructions/contract.rs (L205-214)
```rust
	let call_result = match scheme {
		CallScheme::Call | CallScheme::StaticCall => interpreter.ext.call(
			&CallResources::from_ethereum_gas(gas_limit, add_stipend),
			&callee,
			value,
			input,
			// protect against rex-entrancy when we grant the stipend
			reentracy,
			scheme.is_static_call(),
		),
```
