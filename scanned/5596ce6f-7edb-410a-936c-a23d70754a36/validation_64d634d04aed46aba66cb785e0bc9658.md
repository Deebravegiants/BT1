### Title
`run_call` reentrancy heuristic misclassifies value-transferring stipend calls as `AllowReentry` instead of `AllowNext`, defeating explicit reentrancy protection - ([File: substrate/frame/revive/src/vm/evm/instructions/contract.rs])

### Summary
The heuristic in `run_call` that decides `ReentrancyProtection` level for EVM `CALL`/`STATICCALL` opcodes has a match-arm ordering flaw: any call with `value != 0` is unconditionally classified as `ReentrancyProtection::AllowReentry` (i.e. *no* reentrancy protection at all), regardless of whether `gas_limit == CALL_STIPEND` (2300). The `AllowNext` path is only reached when `value.is_zero()` is `true`, which is precisely the case that matters least for fund-draining attacks. This is the opposite of what the surrounding design/comments intend, and is more severe than the scenario hypothesized in the question (misclassification into `AllowNext`): the actual result is the *weakest* protection, `AllowReentry`, for exactly the value>0 + gas==2300 case (real `.transfer(amount)`/`.send(amount)` calls, or a crafted `.call{value: v, gas: 2300}(...)`).

### Finding Description
`run_call` in `substrate/frame/revive/src/vm/evm/instructions/contract.rs` computes reentrancy protection via: [1](#0-0) 

```rust
let (add_stipend, reentracy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
    {
        (false, _) => (true, ReentrancyProtection::AllowReentry),
        (_, true) => (true, ReentrancyProtection::AllowNext),
        (_, _) => (false, ReentrancyProtection::AllowReentry),
    };
```

The tuple matched is `(value.is_zero(), gas_is_2300)`. Because Rust `match` evaluates arms top-to-bottom and the first arm is `(false, _)` (i.e. `value.is_zero() == false`, meaning `value > 0`), **every** value-transferring call — regardless of `gas_limit` — is caught by this arm first and assigned `ReentrancyProtection::AllowReentry`. The second arm `(_, true)` (the `gas_limit == 2300` stipend heuristic that grants `AllowNext`) can only ever be reached when `value.is_zero()` is `true`, since the `false` case was already consumed by arm 1.

This is inconsistent with the doc comment on `ReentrancyProtection::AllowNext` in `substrate/frame/revive/src/exec.rs`: [2](#0-1) 
which states `AllowNext` "is used for calls that transfer value but restrict gas so that the callee only has a stipend gas amount ... due to gas scale differences that guarantee does not automatically hold in revive and we enforce it explicitly here." The explicit code contradicts this comment: it never applies `AllowNext` to a value-transferring call.

Consequences of getting `AllowReentry` instead of `AllowNext`:
- `PrecompileExt::call` in `exec.rs` only restricts reentry when `allows_reentry == ReentrancyProtection::Strict` (before frame push) or `AllowNext` (after frame push, blocking the callee's own recursive callees): [3](#0-2) 
When `AllowReentry` is passed, neither of these guards trigger — the callee is free to call back into the caller with no reentrancy denial whatsoever.
- The `metering/math.rs` comment/design explicitly acknowledges that Ethereum's 2300-gas physical exhaustion guarantee "does not automatically hold in revive" due to differing gas/weight scales [4](#0-3) , meaning the fallback safety net (running out of gas before completing a reentrant `CALL`) is not reliable either. `AllowNext` was added specifically to compensate for this — but it is bypassed whenever `value != 0`.

For a real-world `.transfer(amount>0)`/`.send(amount>0)` (which Solidity's compiler encodes with `gas_limit == 2300` on the stack) or an attacker-crafted low-level `target.call{value: v, gas: 2300}(data)` (not using `transfer`/`send` syntax, but coincidentally requesting exactly 2300 gas with `value > 0`), the tuple is `(false, true)`. This is caught by arm 1 → `AllowReentry`. The callee's `receive()`/fallback can therefore attempt to re-enter the caller without being blocked by the reentrancy-denial check at all (only limited by whatever weight the stipend actually buys in revive's gas scale, which per the code's own comments is not a reliable barrier).

### Impact Explanation
An unprivileged attacker deploying a malicious receiver contract can receive a `.transfer`/`.send`/crafted-2300-gas value call from a victim contract and attempt a reentrant call into the caller's storage/balance-mutating functions during that call, without the intended `AllowNext` denial being active. If the stipend-equivalent weight budget in revive happens to be sufficient (relative to Ethereum's own 2300-gas limit, which is provably insufficient for a `CALL`), the reentrant call can succeed and mutate caller state (classic checks-effects-interactions violation), enabling fund draining via reentrant withdrawal. This matches the scoped impact in the question.

### Likelihood Explanation
Preconditions are trivial and fully attacker-controlled: deploy any contract whose `receive()`/fallback issues a nested call back into `msg.sender`, and have any counterparty legitimately `.transfer()`/`.send()` value to it (the extremely common Solidity idiom), or explicitly issue `target.call{value: v, gas: 2300}(data)`. No privileged origin, governance, or admin access is required — this is reachable purely through `bare_call`/EVM contract execution, i.e., a normal signed extrinsic invoking a contract that then calls the attacker's contract. This is highly feasible and repeatable in every transaction that sends value via `.transfer`/`.send`/2300-gas calls to an untrusted address.

### Recommendation
Reorder/rewrite the match so that the stipend-gas heuristic is evaluated independently of `value.is_zero()`, e.g.:
```rust
let (add_stipend, reentracy) = if gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND) {
    (true, ReentrancyProtection::AllowNext)
} else if !value.is_zero() {
    (true, ReentrancyProtection::AllowReentry) // or a safer default
} else {
    (false, ReentrancyProtection::AllowReentry)
};
```
so that any call carrying the 2300 stipend gas value — whether or not `value` is zero — is classified `AllowNext`, matching the documented intent, and value-transferring calls without the stipend heuristic get an explicit, reviewed decision rather than defaulting to no protection.

### Proof of Concept
Extend `substrate/frame/revive/src/tests/stipends.rs` with an assertion that inspects actual reentrant state mutation, not just `did_revert()`:
1. Use `ReentrancyAttacker`/`ComplexReceiver`-style fixture whose `receive()` calls back into `attemptTransfer`/a state-mutating function on the caller (as in `Stipends.sol`'s `ReentrancyAttacker`), and add a state-mutating target function (e.g., a public counter or the caller's balance) that the reentrant call would modify if allowed through.
2. Add a test `evm_call_stipend_prevents_value_reentrancy_via_crafted_gas` that:
   - instantiates `StipendTest`,
   - invokes a Solidity helper doing `target.call{value: 1, gas: 2300}(data)` (not `.transfer`/`.send`) where `target` is `ReentrancyAttacker`,
   - asserts that the reentrant call into the caller either returns `ReentranceDenied`/fails, and that the caller's tracked state (e.g. a counter or balance) is unchanged after the outer call completes — i.e., assert no double-spend/state mutation occurred, matching the `Invariant tested` in the question.
3. Instrument/trace (as already partially done per `pr_11227.prdoc`'s trace logs) to confirm which `ReentrancyProtection` variant (`AllowReentry` vs `AllowNext`) was actually selected for the value>0 + gas==2300 case, and assert it is `AllowNext`.

### Citations

**File:** substrate/frame/revive/src/vm/evm/instructions/contract.rs (L192-203)
```rust
) -> ControlFlow<Halt> {
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

**File:** substrate/frame/revive/src/exec.rs (L134-141)
```rust
	/// Activate reentrancy protection where the direct callee can be the same contract as the
	/// caller but none of the recursive callees of the callee must be the caller.
	///
	/// This is used for calls that transfer value but restrict gas so that the callee only has a
	/// stipend gas amount. In Ethereum that is not sufficient for the callee to make another call.
	/// However, due to gas scale differences that guarantee does not automatically hold in revive
	/// and we enforce it explicitly here.
	AllowNext,
```

**File:** substrate/frame/revive/src/exec.rs (L2163-2192)
```rust
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
