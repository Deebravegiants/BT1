### Title
Reentrancy stipend heuristic never engages `AllowNext` protection for real value transfers - (File: substrate/frame/revive/src/vm/evm/instructions/contract.rs)

### Summary
In `run_call`, the match arm that decides between `ReentrancyProtection::AllowReentry` and `ReentrancyProtection::AllowNext` is ordered so that any non-zero-value call (`value.is_zero() == false`) is caught by the first arm `(false, _)` regardless of the gas limit, before the `gas_limit == CALL_STIPEND` (2300) arm is ever evaluated. This means the classic Solidity `.transfer()`/`.send()` pattern — non-zero `value` with `gas_limit == 2300` — always resolves to `ReentrancyProtection::AllowReentry`, never to the intended `AllowNext` guard, defeating the stipend-based reentrancy protection entirely for exactly the case it was designed to protect.

### Finding Description
`run_call` at [1](#0-0)  computes `(add_stipend, reentrancy)` via:

```rust
let (add_stipend, reentracy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
    {
        (false, _) => (true, ReentrancyProtection::AllowReentry),
        (_, true) => (true, ReentrancyProtection::AllowNext),
        (_, _) => (false, ReentrancyProtection::AllowReentry),
    };
```

Rust `match` evaluates arms top-to-bottom, and `(false, _)` is a wildcard on the second tuple element. Because `value.is_zero()` is the *first* tuple field, any call with non-zero `value` — including the canonical `.transfer()`/`.send()` case where `value > 0` and `gas_limit == 2300` — matches arm 1 unconditionally and is assigned `ReentrancyProtection::AllowReentry`, i.e. full reentrancy is allowed. The `(_, true) => AllowNext` arm is only reachable when `value.is_zero()` is `true`, i.e. **no value is transferred at all** — a scenario that poses no fund-draining risk and does not correspond to Solidity's stipend-limited transfer pattern described in the code's own comment ("For zero-value transfer/send, solc injects `gas_limit = 2300`" — which is itself a mischaracterization, since `.transfer`/`.send` always move non-zero value).

This is called from the `CALL` opcode handler at [2](#0-1) , which is reachable by any unprivileged contract executing EVM bytecode compiled from Solidity using `.transfer()`/`.send()`. Consequently, when a victim contract does `payable(attacker).transfer(amount)`, the interpreter grants `ReentrancyProtection::AllowReentry` to the sub-call into `attacker`'s `receive()`/fallback, rather than the intended `AllowNext` restriction. The attacker's fallback can therefore freely re-enter the victim (e.g. call `withdraw()` again) before the victim's balance-decrement completes, enabling the classic checks-effects-interactions reentrancy drain — exactly the attack the stipend heuristic was supposed to prevent.

### Impact Explanation
Any EVM-compatible contract deployed on `pallet_revive` that follows the common (and previously believed "safe under 2300-gas stipend") pattern of using `.transfer()`/`.send()` before updating internal balances is exposed to classic reentrancy. An attacker contract can drain native token balances tracked by the victim contract by repeatedly re-entering a withdrawal function during the stipend-limited callback, since the reentrancy guard that should limit the callback to non-reentrant "AllowNext" behavior is never actually applied in the non-zero-value branch.

### Likelihood Explanation
High feasibility for any unprivileged attacker: no privileged origin, proxy, or governance is required. The attacker only needs to deploy a malicious contract with a `receive()`/fallback that calls back into the victim, and get the victim to call `.transfer()`/`.send()` to it (e.g., by being a legitimate participant of a payout/withdrawal contract). This is a pure logic/ordering bug in match-arm evaluation, deterministically reproducible on every call matching the pattern, not a corner-case race.

### Recommendation
Fix the match arm ordering/condition so that the stipend heuristic is evaluated with correct precedence — the `AllowNext` protection must apply specifically when `value` is non-zero **and** `gas_limit == CALL_STIPEND`, not be shadowed by a value-non-zero wildcard arm. For example:

```rust
let (add_stipend, reentrancy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND)) {
        (false, true) => (true, ReentrancyProtection::AllowNext),
        (false, false) => (true, ReentrancyProtection::AllowReentry),
        (true, _) => (false, ReentrancyProtection::AllowReentry),
    };
```
This ensures the stipend-limited, value-transferring call path (the actual `.transfer()`/`.send()` pattern) receives the restrictive `AllowNext` reentrancy protection, while unrelated zero-value calls are unaffected.

### Proof of Concept
Extend `substrate/frame/revive/src/tests/stipends.rs::evm_call_stipend_prevents_transfer_reentrancy` (referenced at [3](#0-2) ) with a victim/attacker pair where:
1. Victim contract holds a balance mapping; `withdraw()` performs `balance[msg.sender] = 0;` **after** calling `.transfer(msg.sender, amount)` (vulnerable, non-CEI ordering, intentionally used to test the runtime-level stipend guard rather than relying on contract-level CEI).
2. Attacker's `receive()` re-enters `victim.withdraw()`.
3. Assert that the second, reentrant `withdraw()` call executed under `AllowNext`/stipend gas is rejected/blocked (i.e., its state-changing external call fails due to reentrancy protection), and that the victim's final on-chain balance for the attacker equals zero after a single legitimate withdrawal (no double-spend).
4. Given the current match-arm bug, this test would currently fail: the reentrant call succeeds because `ReentrancyProtection::AllowReentry` is granted instead of `AllowNext`, allowing the double withdrawal and draining more funds than were deposited.

### Citations

**File:** substrate/frame/revive/src/vm/evm/instructions/contract.rs (L108-128)
```rust
pub fn call<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	let [gas_limit, to, value] = interpreter.stack.popn()?;
	let to = to.into_address();
	let has_transfer = !value.is_zero();
	if interpreter.ext.is_read_only() && has_transfer {
		return ControlFlow::Break(Error::<E::T>::StateChangeDenied.into());
	}
	let (input, return_memory_range) = get_memory_in_and_out_ranges(interpreter)?;
	let scheme = CallScheme::Call;
	charge_call_gas(interpreter, to, scheme, input.len(), value)?;

	run_call(
		interpreter,
		to,
		gas_limit,
		interpreter.memory.slice(input).to_vec(),
		scheme,
		value,
		return_memory_range,
	)
}
```

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

**File:** substrate/frame/revive/src/tests/stipends.rs (L1-1)
```rust
// This file is part of Substrate.
```
