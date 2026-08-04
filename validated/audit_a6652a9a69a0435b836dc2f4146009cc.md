### Title
Reentrancy stipend protection (`AllowNext`) is unreachable for any value-transferring `CALL`, defeating Solidity's `.transfer()`/`.send()` reentrancy guarantee - (File: substrate/frame/revive/src/vm/evm/instructions/contract.rs)

### Summary
In `run_call`, the tuple match that decides between `ReentrancyProtection::AllowNext` and `ReentrancyProtection::AllowReentry` is ordered so that any non-zero `value` immediately matches the wildcard arm `(false, _) => (true, AllowReentry)`, before the `gas_limit == CALL_STIPEND` check is ever evaluated. This means `AllowNext` can only ever be selected when `value.is_zero()` is `true`, i.e. for zero-value calls - never for the actual value-transferring `.transfer()`/`.send()` calls the heuristic was built to protect. As a result, callees receiving Ether-equivalent value via a normal EVM `CALL` are always granted unrestricted `AllowReentry`, allowing them to re-enter the calling contract mid-execution.

### Finding Description
`run_call` computes reentrancy mode as: [1](#0-0) 

The match is on `(value.is_zero(), gas_limit == CALL_STIPEND)`. Because Rust matches arms in order and `(false, _)` is a wildcard on the second element, **any** non-zero `value` is captured by the first arm regardless of `gas_limit`, producing `AllowReentry`. The `(_, true) => AllowNext` arm is only reachable when the first arm didn't match, i.e. `value.is_zero() == true`.

Per the project's own PR documentation (`prdoc/stable2603/pr_11227.prdoc`), real Solidity semantics are:
- `target.transfer(amount)` / `target.send(amount)` with `amount > 0`: compiler passes `gas_limit = 0`; the EVM/runtime is expected to add the 2300 stipend and restrict the callee to just that gas — this is the case that must be protected by `AllowNext`.
- `target.transfer(0)` / `target.send(0)`: compiler explicitly passes `gas_limit = 2300` for a *zero-value* call.
- `target.call{value: v}("")`: forwards all remaining gas, no stipend restriction — correctly gets `AllowReentry`.

The comment in the code even documents the intent ("This is required to implement reentrancy protection for simple transfers with call stipends" — see `exec.rs` `ReentrancyProtection::AllowNext` docs), but the implementation only triggers `AllowNext` for the zero-value corner case, not for the primary non-zero-value `.transfer()`/`.send()` case it was meant to guard. `AllowNext` is therefore effectively dead code for the scenario that matters, and every non-zero-value `CALL` — whatever `gas_limit` the caller specifies, including `2300` — gets `AllowReentry`.

Downstream in `exec.rs`, `AllowReentry` leaves `top_frame_mut().allows_reentry` untouched (only `Strict` sets it `false` before the frame, and only `AllowNext` sets it `false` after the frame): [2](#0-1)  So the callee frame remains fully re-entrant into the caller.

The docs explain why this matters specifically for revive: unlike real Ethereum where 2300 gas is provably insufficient to perform another `CALL`, revive's weight-based gas scale does not guarantee that the stipend is insufficient for a reentrant call, hence the deliberate addition of the `AllowNext` mechanism (see `ReentrancyProtection` enum docs, `exec.rs` lines 134-141 and `prdoc/pr_10166.prdoc` lines 38-40). Because the match bug makes `AllowNext` unreachable for the real transfer case, that safety net never activates.

### Impact Explanation
Any EVM-compatible contract deployed on pallet-revive that uses the idiomatic Solidity reentrancy-safe pattern `payable(x).transfer(amount)` or `.send(amount)` for value transfers does **not** get the reentrancy protection Solidity developers rely on. An attacker-controlled recipient contract's fallback/receive function is executed under `AllowReentry` and can re-enter the calling (victim) contract before the victim finishes its post-transfer state updates (e.g. balance decrement), enabling classic reentrancy fund-draining attacks (DAO-style) against otherwise "safe" contracts, in violation of the invariant that user-controlled assets must remain fully backed and cannot be stolen.

### Likelihood Explanation
This is trivially and deterministically reachable: any unprivileged user can deploy an attacker contract with a `receive()`/fallback that calls back into the victim, and interact with any pre-existing victim contract that transfers Ether via `.transfer()`/`.send()`. No special gas_limit crafting is even required — solc's normal compiled output for `.transfer(amount)` (`gas_limit = 0`, `value > 0`) already falls into the buggy `AllowReentry` arm. The bug is 100% reproducible and not probabilistic.

### Recommendation
Fix the match ordering/logic in `run_call` so that `AllowNext` protection applies whenever the effective gas granted to the callee is limited to just the stipend, i.e. for value-transferring calls where `gas_limit == 0` (compiler-inserted automatic stipend) or `gas_limit == CALL_STIPEND` (explicit `transfer(0)`/`send(0)`), rather than gating `AllowNext` behind `value.is_zero()`. Concretely, restructure the match to check `gas_limit == CALL_STIPEND` (or `gas_limit == 0` combined with `!value.is_zero()`) independent of whether `value` is zero, and only fall back to `AllowReentry` for calls that forward non-stipend gas amounts (e.g. `.call{value: v}("")`).

### Proof of Concept
Rust integration test in `substrate/frame/revive/src/exec/tests.rs` (or EVM fixture-based test alongside `evm_call_stipends_work_for_*`):
1. Deploy `Victim` contract with `withdraw()`: `balances[msg.sender] -= amount;` executed *after* `payable(msg.sender).transfer(amount);` (mirrors the classic pattern relying on stipend protection).
2. Deploy `Attacker` contract whose `receive()` calls back into `Victim.withdraw()` again.
3. Fund `Victim`, call `Attacker` to trigger `Victim.withdraw()`.
4. Assert: reentrant call into `withdraw()` from `Attacker.receive()` either fails with `ReentranceDenied` (expected/fixed behavior) or succeeds and drains more than the attacker's legitimate balance (current buggy behavior).
5. Unit-level assertion directly on `run_call`'s heuristic: for `value != 0` and `gas_limit == CALL_STIPEND (2300)`, assert the selected `ReentrancyProtection` is `AllowNext`, not `AllowReentry` — this assertion fails against current code, proving the bug.

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

**File:** substrate/frame/revive/src/exec.rs (L2167-2192)
```rust
		if allows_reentry == ReentrancyProtection::Strict {
			self.top_frame_mut().allows_reentry = false;
		}

		// We reset the return data now, so it is cleared out even if no new frame was executed.
		// This is for example the case for balance transfers or when creating the frame fails.
		*self.last_frame_output_mut() = Default::default();

		let try_call = || {
			// Enable read-only access if requested; cannot disable it if already set.
			let is_read_only = read_only || self.is_read_only();

			// We can skip the stateful lookup for pre-compiles.
			let dest = if <AllPrecompiles<T>>::get::<Self>(dest_addr.as_fixed_bytes()).is_some() {
				T::AddressMapper::to_fallback_account_id(dest_addr)
			} else {
				T::AddressMapper::to_account_id(dest_addr)
			};

			if !self.allows_reentry(&dest) {
				return Err(<Error<T>>::ReentranceDenied.into());
			}

			if allows_reentry == ReentrancyProtection::AllowNext {
				self.top_frame_mut().allows_reentry = false;
			}
```
