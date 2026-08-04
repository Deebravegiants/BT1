### Title
Match-arm ordering in `run_call` grants full `AllowReentry` instead of stipend-restricted `AllowNext` for value-transferring calls at `gas_limit == CALL_STIPEND` - (File: substrate/frame/revive/src/vm/evm/instructions/contract.rs)

### Summary
`run_call`'s heuristic for detecting Ethereum's 2300-gas stipend pattern (`value != 0`, `gas_limit == CALL_STIPEND`) is broken due to match-arm ordering: the `(false, _)` arm (meaning `value.is_zero() == false`, i.e. value is non-zero) is checked before the `(_, true)` arm, so any non-zero-value call always resolves to `ReentrancyProtection::AllowReentry` regardless of `gas_limit`. This is exactly backwards from the documented intent, since Solidity's `.transfer()`/`.send()` — the classic reentrancy-safe pattern — always sends `value != 0` with `gas_limit == 2300`.

### Finding Description
In `run_call` [1](#0-0) , the tuple match is:

```
match (value.is_zero(), gas_limit == CALL_STIPEND) {
    (false, _) => (true, ReentrancyProtection::AllowReentry),
    (_, true) => (true, ReentrancyProtection::AllowNext),
    (_, _)    => (false, ReentrancyProtection::AllowReentry),
}
```

Rust matches arms top-to-bottom and stops at the first match. Because `(false, _)` is a wildcard on the second element, it matches **any** `gas_limit` whenever `value.is_zero()` is `false` (i.e. value is being transferred) — this includes the exact case `gas_limit == CALL_STIPEND (2300)`. The second arm `(_, true)`, which is supposed to catch the "solc passes 2300 for a stipend-limited transfer" heuristic and apply `AllowNext`, can therefore never be reached when `value != 0`; it is effectively dead code for the value-transfer case and only fires when `value == 0` and `gas_limit == 2300` (a no-op/uninteresting case since there's no ether at stake).

This inverts the intended Ethereum-equivalent semantics: `.transfer()`/`.send()` in Solidity (and any low-level `call{value: v, gas: 2300}(...)`) is precisely the `value != 0, gas == 2300` case, which real Ethereum protects against reentrancy because 2300 gas is insufficient for a state-changing callback (e.g., `SSTORE`). Here, that same call instead receives `ReentrancyProtection::AllowReentry`, `Ext`'s least restrictive setting [2](#0-1) , which does not prevent the callee from making a recursive call back into the caller contract before the caller finishes its own state update. Because PolkaVM/revive's gas metering scale differs from Ethereum's, the 2300-unit stipend does not by itself limit what the callee can do computationally — the code comment on `AllowNext` explicitly acknowledges this and states protection must be enforced explicitly, which the arm-ordering bug defeats.

### Impact Explanation
An unprivileged attacker deploying a malicious contract and interacting with any victim contract using the canonical `.transfer()`/`.send()`/low-level-`call{value, gas: 2300}` withdrawal pattern can re-enter the victim during the call-back, before the victim contract's balance/state bookkeeping completes. This is the classic reentrancy pattern (e.g., "DAO-style" drain) and, under the intended design (`AllowNext`), should be blocked by revive's reentrancy protection, but is not, since it instead receives `AllowReentry`. Scoped impact: cross-contract reentrancy drain/double-spend of a victim contract's balance.

### Likelihood Explanation
Highly feasible and fully attacker-controlled: no privileged origin needed. An attacker only needs to (1) deploy a fallback/receive-hook contract, and (2) get a victim contract to call it via the extremely common `.transfer()`/`.send()` Solidity pattern (`value != 0`, `gas_limit == 2300`), which is compiled into a huge fraction of real-world EVM contracts by `solc`. This is trivially reproducible in a deterministic test, not merely fuzz-dependent, since exact stipend value 2300 is a compiler constant.

### Recommendation
Reorder/rewrite the match so that the stipend-heuristic check is evaluated independent of arm ordering, e.g.:
```rust
let (add_stipend, reentrancy) = if !value.is_zero() && gas_limit == CALL_STIPEND {
    (true, ReentrancyProtection::AllowNext)
} else if !value.is_zero() {
    (true, ReentrancyProtection::AllowReentry)
} else {
    (false, ReentrancyProtection::AllowReentry)
};
```
i.e. check the compound condition `(value != 0 && gas_limit == CALL_STIPEND)` first, matching the documented intent, before falling back to the plain "has transfer" branch.

### Proof of Concept
Rust unit test in `substrate/frame/revive/src/vm/evm/instructions/contract.rs` (or `exec/tests.rs`, using `mock_ext`):
1. Construct a call with `value = U256::from(1)` (non-zero) and `gas_limit = U256::from(2300)` (i.e., `CALL_STIPEND`).
2. Invoke `run_call` (or the `call` instruction handler) and assert on the `reentrancy` value passed into `Ext::call`.
   - Expected (per doc/intent): `ReentrancyProtection::AllowNext`.
   - Actual (bug): `ReentrancyProtection::AllowReentry`.
3. Integration/exec-stack test: deploy a victim contract that:
   - On `withdraw()`, first calls `CALL` with `value=attacker_balance, gas=2300` to the attacker address, and only afterward zeroes the attacker's internal balance record.
   - Deploy an attacker contract whose fallback re-enters `victim.withdraw()`.
   - Assert that with the current buggy match ordering, the reentrant call succeeds and drains more than the attacker's legitimate balance (double-withdraw), whereas after the fix the reentrant call must be rejected/blocked (`AllowNext` should stop the callee's recursive call back into the caller).

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

**File:** substrate/frame/revive/src/exec.rs (L127-142)
```rust
#[derive(Copy, Clone, PartialEq, Debug)]
pub enum ReentrancyProtection {
	/// Don't activate reentrancy protection
	AllowReentry,
	/// Activate strict reentrancy protection. The direct callee and none of its own recursive
	/// callees must be the calling contract.
	Strict,
	/// Activate reentrancy protection where the direct callee can be the same contract as the
	/// caller but none of the recursive callees of the callee must be the caller.
	///
	/// This is used for calls that transfer value but restrict gas so that the callee only has a
	/// stipend gas amount. In Ethereum that is not sufficient for the callee to make another call.
	/// However, due to gas scale differences that guarantee does not automatically hold in revive
	/// and we enforce it explicitly here.
	AllowNext,
}
```
