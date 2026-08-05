### Title
`AllowNext` reentrancy protection is bypassed for real-world stipend transfers because of match-arm ordering on `value.is_zero()` - ([File: substrate/frame/revive/src/vm/evm/instructions/contract.rs])

### Summary
The EVM CALL/STATICCALL stipend-detection heuristic in `run_call` (`substrate/frame/revive/src/vm/evm/instructions/contract.rs:193-203`) only applies `ReentrancyProtection::AllowNext` when the transferred `value` is zero AND `gas_limit == CALL_STIPEND` (2300). The classic Solidity `.transfer()`/`.send()` pattern (which is exactly what this mechanism was built to defend against, per the `ReentrancyProtection::AllowNext` doc comment in `exec.rs:134-141`) sends a non-zero `value` together with `gas_limit == 2300`. Because the match arm `(false, _) => (true, ReentrancyProtection::AllowReentry)` is evaluated first and matches whenever `value != 0`, this exact real-world case falls through to `AllowReentry` — i.e. no reentrancy protection at all — defeating the purpose of the guard for the very case it was designed to close.

### Finding Description
`run_call` builds the reentrancy mode from a tuple match:
```rust
let (add_stipend, reentracy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
    {
        (false, _) => (true, ReentrancyProtection::AllowReentry),
        (_, true) => (true, ReentrancyProtection::AllowNext),
        (_, _) => (false, ReentrancyProtection::AllowReentry),
    };
``` [1](#0-0) 

Solidity's `address.transfer(amount)` / `address.send(amount)` compile to a low-level call with `gas = 2300` and `value = amount` (non-zero in the typical withdraw case). Because Rust's pattern matching evaluates arms top-to-bottom and `value.is_zero()` is `false` here, the first arm `(false, _)` matches unconditionally regardless of the gas-limit value, so `ReentrancyProtection::AllowReentry` (no protection) is selected instead of `AllowNext`. The `AllowNext` branch is only reachable when `value == 0` *and* `gas_limit == 2300` — a call shape that does not correspond to any typical Solidity stipend transfer since `.transfer`/`.send` always carry the value being paid out.

This is the exact case the enum doc explicitly targets:
```rust
/// This is used for calls that transfer value but restrict gas so that the callee only has a
/// stipend gas amount. In Ethereum that is not sufficient for the callee to make another call.
/// However, due to gas scale differences that guarantee does not automatically hold in revive
/// and we enforce it explicitly here.
AllowNext,
``` [2](#0-1) 

The enforcement mechanism itself (`allows_reentry` flag set on the caller's frame before pushing the callee frame, checked against all frames on the stack by `account_id`) is correct and effective when actually invoked — see `PrecompileExt::call` in `exec.rs:2160-2192` and `allows_reentry` in `exec.rs:1890-1893`. The bug is that the EVM front-end at `contract.rs:193-203` fails to select this protection for the primary target scenario ("transfer value but restrict gas"), because the match on `value.is_zero()` short-circuits before the gas-limit check can matter.

### Impact Explanation
An attacker contract can implement a fallback/receive function that reenters a victim contract's withdraw logic during the 2300-gas stipend call triggered by the victim's `.transfer(amount)`/`.send(amount)` (non-zero value), since `AllowReentry` (no protection) is applied instead of the intended `AllowNext`. If the victim uses a naive interaction-before-effects withdraw pattern, the attacker can re-enter and drain more funds than its entitled balance — classic reentrancy fund theft — exactly the scoped impact in the question, and it defeats revive's compensating control that was specifically added (per `ReentrancyProtection::AllowNext`'s doc) to make up for the fact that a 2300-gas stipend in revive's execution model is not actually sufficient to prevent reentrancy the way it is in real Ethereum.

Note: this does not amount to `Strict` mode being bypassed (contracts that explicitly opt into `Strict`/non-2300-gas calls via `.call{gas: X}()` are unaffected), and it does not affect the PVM/ink! `ALLOW_REENTRY` flag path in `vm/pvm.rs`, which is a separate, explicit, developer-opt-in mechanism unrelated to this heuristic.

### Likelihood Explanation
High feasibility and fully attacker-controlled: any Solidity contract compiled to PVM/EVM bytecode for pallet-revive that uses `.transfer()` or `.send()` for payouts (an extremely common pattern, effectively the majority of legacy withdraw-pattern contracts) is affected. No privileged action is required — an unprivileged user deploys a vulnerable victim (naive withdraw) and an attacker contract, then calls `withdraw()` through a normal extrinsic/`eth_transact`. The vulnerability is deterministic and repeatable on every call matching the pattern (non-zero value + `gas_limit == 2300`).

### Recommendation
Fix the match logic so the stipend-detection (gas_limit == CALL_STIPEND) is checked independent of whether `value` is zero, and `AllowNext`/stipend accounting is applied whenever `gas_limit == CALL_STIPEND`, regardless of `value.is_zero()`. E.g.:
```rust
let is_stipend = gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND);
let (add_stipend, reentracy) = if is_stipend {
    (true, ReentrancyProtection::AllowNext)
} else if !value.is_zero() {
    (true, ReentrancyProtection::AllowReentry)
} else {
    (false, ReentrancyProtection::AllowReentry)
};
```
Add regression tests asserting that a non-zero-value call with `gas_limit == CALL_STIPEND` triggers `ReentrancyProtection::AllowNext` (i.e., `ReentranceDenied` on reentry into the caller), matching the existing `call_deny_reentry`/`call_reentry_direct_recursion` test patterns in `exec/tests.rs`.

### Proof of Concept
Rust integration test in `substrate/frame/revive/src/exec/tests.rs` (or an EVM-bytecode fixture test under `pallet-revive-fixtures`):
1. Deploy `Victim` fixture whose `withdraw()` PVM/EVM bytecode performs a `CALL` with `value = attacker_balance`, `gas_limit = CALL_STIPEND (2300)` to `msg.sender`, mimicking Solidity `.transfer()`.
2. Deploy `Attacker` fixture whose fallback (invoked by the stipend call) calls back into `Victim.withdraw()`.
3. Fund `Victim` with balance for two legitimate withdrawals' worth of ETH/token accounting, but give `Attacker` entitlement to only one.
4. Call `Victim.withdraw()` from `Attacker`.
5. Assert: with the current buggy match arms, the attacker's reentrant call into `Victim.withdraw()` succeeds (`Ok`) and `Victim`'s balance is drained beyond `Attacker`'s entitlement — proving `AllowReentry` (no protection) is active instead of `AllowNext`.
6. After applying the recommended fix, assert the reentrant call returns `Error::<Test>::ReentranceDenied` and the final balance change equals exactly one entitled withdrawal.

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
