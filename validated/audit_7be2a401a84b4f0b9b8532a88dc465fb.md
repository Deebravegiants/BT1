### Title
Reentrancy stipend protection bypass: nonzero-value `.transfer()`/`.send()` calls get `AllowReentry` instead of `AllowNext` due to match-arm ordering - (`substrate/frame/revive/src/vm/evm/instructions/contract.rs`)

### Summary
`run_call` in the EVM-compatibility layer of `pallet-revive` is supposed to apply `ReentrancyProtection::AllowNext` whenever a `CALL`/`STATICCALL` is made with the Solidity 2300-gas stipend (the pattern used by `.transfer()`/`.send()`), because the code explicitly documents that Ethereum's implicit "2300 gas is too little to reenter" guarantee "does not automatically hold in revive" due to gas-scale differences. The match-arm ordering, however, causes every call with a **nonzero** value — which is exactly what `.transfer()`/`.send()` produce (value > 0, gas_limit == 2300) — to be caught by the first arm and classified as `ReentrancyProtection::AllowReentry` instead, silently disabling the intended explicit reentrancy guard for the real-world idiom it was built to protect.

### Finding Description
The reentrancy-mode selection lives in `run_call`: [1](#0-0) 

```rust
let (add_stipend, reentracy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
    {
        (false, _) => (true, ReentrancyProtection::AllowReentry),
        // Heuristic: detect when solc passes `gas_limit = 2300` (the call stipend).
        // For zero-value transfer/send, solc injects `gas_limit = 2300` explicitly.
        (_, true) => (true, ReentrancyProtection::AllowNext),
        (_, _) => (false, ReentrancyProtection::AllowReentry),
    };
```

Rust `match` arms are evaluated top-to-bottom. Solidity's `.transfer(amount)` and `.send(amount)` idioms compile to a `CALL` with **both** a nonzero `value` (the amount being sent) **and** `gas_limit == 2300` (`CALL_STIPEND`). For this exact tuple, `value.is_zero()` is `false`, so the first arm `(false, _)` matches unconditionally regardless of the gas limit, and the call is classified `ReentrancyProtection::AllowReentry`. The second arm `(_, true)`, which is the one carrying the explicit stipend-reentrancy fix (`AllowNext`), is only reachable when `value.is_zero()` is `true` — i.e. only for zero-value stipend calls, not the classic value-transferring `.transfer()`/`.send()` pattern the PR (see `pr_10166.prdoc`) was written to fix.

This selected `reentracy` value is passed straight into `PrecompileExt::call`: [2](#0-1) 

Where `ReentrancyProtection::Strict` sets `top_frame_mut().allows_reentry = false` *before* the `allows_reentry(&dest)` check (blocking any re-entrance into the calling frame, direct or indirect), and `AllowNext` sets it *after* the check (allowing this one call, but blocking any subsequent re-entrant call back into the caller for the remainder of the sub-call). `AllowReentry` performs neither action, leaving the caller frame's `allows_reentry` flag untouched (`true`), so a callee (or its fallback) is completely free to call back into the caller mid-execution.

The prdoc for the reentrancy redesign explicitly states the intended risk model this was built to close: [3](#0-2) 

> "`AllowNext` allows to re-enter the same contract but only for the next frame. This is required to implement reentrancy protection for simple transfers with call stipends" ... "due to gas scale differences that guarantee does not automatically hold in revive and we enforce it explicitly here" (comment at line 139-140 of `exec.rs`, `ReentrancyProtection::AllowNext` doc).

Because the maintainers themselves acknowledge that relying on gas-scale-derived weight exhaustion alone is *not* a reliable reentrancy defense in revive, the explicit `AllowNext` enforcement was added as the real protection mechanism. The match-arm bug means this mechanism never activates for the real, non-zero-value `.transfer()`/`.send()` calls it targets — only for the less common zero-value stipend call pattern.

The existing regression tests (`evm_call_stipend_prevents_transfer_reentrancy`, `evm_call_stipend_prevents_send_reentrancy`) happen to pass, but only because their `ReentrancyAttacker.receive()` fixture itself issues a *further* external `CALL`, whose own weight-mapped-gas overhead exceeds the tiny stipend-derived weight budget — an incidental, gas-scale-dependent effect, not the intended explicit `AllowNext` guard (which never triggers for these nonzero-value cases due to the bug). This matches the code's own caveat that the implicit gas-exhaustion protection "does not automatically hold" — it is not a load-bearing guarantee, and any reentrant call cheap enough (in mapped-weight terms) to fit inside the stipend's weight budget — e.g. a direct storage read/compare in a check-then-transfer withdraw pattern rather than a further external `CALL` — bypasses both defenses simultaneously.

### Impact Explanation
A contract using the classic Solidity checks-effects-interactions violation (`balance` check, `msg.sender.transfer(amount)`/`.send(amount)`, then decrement balance) is only protected from reentrancy by (a) the incidental weight cost of the reentrant path exceeding the mapped stipend budget, or (b) explicit `AllowNext`/`Strict` reentrancy checks. Because the match-arm bug routes exactly this real-world call shape to `AllowReentry`, protection (b) never applies, leaving only the fragile, maintainer-acknowledged-as-unreliable weight-based protection (a). If a fallback's reentrant call into `withdraw()` is cheap enough at revive's gas/weight exchange rate to fit within the stipend budget, the attacker can re-enter `withdraw()` before the balance is decremented, draining more funds than they are entitled to — a direct fund-theft double-spend of the storage-tracked balance.

### Likelihood Explanation
The precondition is only that an EVM-mode contract be deployed with a vulnerable check-then-transfer withdrawal pattern and be called with `.transfer()`/`.send()` (the standard Solidity idiom for value transfers, still widely used) — no privileged access or unusual origin is required; the attack is fully reachable via an ordinary `eth_call`/extrinsic-dispatched contract call from any unprivileged account. The severity is gated purely by whether the reentrant call's mapped weight cost fits the stipend-derived budget for a given contract/runtime gas-to-weight configuration, which is data- and config-dependent rather than a hard barrier — making this a genuine, reachable gap rather than a purely theoretical one.

### Recommendation
Fix the match-arm ordering/logic in `run_call` so that "nonzero value AND `gas_limit == CALL_STIPEND`" is classified as `ReentrancyProtection::AllowNext` (matching real Solidity `.transfer()`/`.send()` semantics), and only truly generic nonzero-value calls with other gas limits fall back to `AllowReentry`, e.g.:
```rust
let (add_stipend, reentracy) = match (value.is_zero(), is_stipend_gas) {
    (_, true) => (true, ReentrancyProtection::AllowNext),
    (false, false) => (true, ReentrancyProtection::AllowReentry),
    (true, false) => (false, ReentrancyProtection::AllowReentry),
};
```

### Proof of Concept
Rust integration test extending `substrate/frame/revive/src/tests/stipends.rs`:
1. Deploy a fixture contract `Bank` with a checks-effects-interactions-violating `withdraw()` (checks `balances[msg.sender] >= amount`, then does `msg.sender.transfer(amount)` — nonzero value + 2300 gas — and only afterward sets `balances[msg.sender] -= amount`).
2. Deploy `ReentrantAttacker` whose `receive()` fallback, on being sent value, directly calls back `Bank.withdraw(amount)` again (not a nested arbitrary external call, but a cheap direct reentry designed to fit the stipend weight budget).
3. Fund `Bank`, credit `ReentrantAttacker` a legitimate balance of `amount`, call `withdraw(amount)` once from `ReentrantAttacker`.
4. Assert: after execution, `Bank`'s recorded balance for `ReentrantAttacker` did not go negative/underflow-wrapped, and total ETH paid out to `ReentrantAttacker` does not exceed its original credited balance (`payout <= amount`), i.e. the reentrant `withdraw()` call must be rejected with `ReentranceDenied` rather than executing to completion.
5. Verify the reentrant call is denied with `Error::<Test>::ReentranceDenied` by adding a debug assertion inside the fixture's fallback, or check `did_revert()`/failure of the inner call return value.

Expected result with current (buggy) code: attacker balance is spent more than once if the reentrant `withdraw()` call fits within the stipend-derived weight, since `reentracy == AllowReentry` for the outer `.transfer()` call. Expected result after fix: inner reentrant call returns `ReentranceDenied` because `AllowNext` correctly flags the calling frame (`Bank`) as non-reenterable for the duration of the stipend call.

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

**File:** substrate/frame/revive/src/exec.rs (L2160-2192)
```rust
		allows_reentry: ReentrancyProtection,
		read_only: bool,
	) -> Result<(), ExecError> {
		// Before pushing the new frame: Protect the caller contract against reentrancy attacks.
		// It is important to do this before calling `allows_reentry` so that a direct recursion
		// is caught by it.

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

**File:** prdoc/stable2603/pr_10166.prdoc (L38-41)
```text
    - Re-entrancy protection now has three modes: no protection, `Strict` protection and `AllowNext`
      - `AllowNext` allows to re-enter the same contract but only for the next frame. This is required to implement reentrancy protection for simple transfers with call stipends
      - For `Strict` protection we set `allows_reentry` of the caller to `false` before the creation of the new frame, for `AllowNext` we to it after the creation
    - We define the max block gas as `u64::MAX` (as discussed with @pgherveou)
```
