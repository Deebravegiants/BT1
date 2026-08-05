### Title
Reentrancy stipend heuristic in `run_call` never applies `AllowNext` protection to non-zero value transfers, granting full `AllowReentry` even when gas is capped at `CALL_STIPEND` - (File: substrate/frame/revive/src/vm/evm/instructions/contract.rs)

### Summary
`run_call` in `substrate/frame/revive/src/vm/evm/instructions/contract.rs` decides reentrancy protection via a match on `(value.is_zero(), gas_limit == CALL_STIPEND)`. Because the first arm `(false, _)` matches on any non-zero value regardless of the second tuple element, a call that transfers non-zero value with `gas_limit == CALL_STIPEND` (2300) is captured by the unconditional non-zero-value arm and always receives `ReentrancyProtection::AllowReentry`, never the intended `AllowNext` protection.

### Finding Description
The relevant logic is: [1](#0-0) 

```
let (add_stipend, reentracy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
    {
        (false, _) => (true, ReentrancyProtection::AllowReentry),
        (_, true) => (true, ReentrancyProtection::AllowNext),
        (_, _) => (false, ReentrancyProtection::AllowReentry),
    };
```

Rust `match` evaluates arms in order. The first arm `(false, _)` fires whenever `value.is_zero()` is `false` — i.e. whenever the call transfers non-zero value — irrespective of the second field (`gas_limit == CALL_STIPEND`). Consequently, the second arm `(_, true)`, which grants `ReentrancyProtection::AllowNext`, is structurally unreachable for any call with non-zero value: it can only ever fire when `value.is_zero()` is `true` (i.e. `value == 0`).

The doc comment on `ReentrancyProtection::AllowNext` explicitly states the intended purpose: [2](#0-1) 

"This is used for calls that transfer value but restrict gas so that the callee only has a stipend gas amount... due to gas scale differences that guarantee does not automatically hold in revive and we enforce it explicitly here." This describes precisely a value-transferring call with `gas_limit == CALL_STIPEND` — yet the actual match-arm ordering routes exactly that case to the unconditional non-zero-value arm and grants `AllowReentry` instead.

This is corroborated by the project's own PR documentation, which states the heuristic is only exercised for the *zero-value* case: [3](#0-2) 

An attacker (any unprivileged contract deployer/caller) can trigger this by issuing a `CALL` opcode with non-zero `value` and `gas_limit == 2300` (i.e. Solidity `target.call{value: v, gas: 2300}("")`, or the classic `target.transfer(v)`/`target.send(v)` pattern which the EVM/solc handles with an implicit or explicit stipend). In genuine Ethereum, 2300 gas is insufficient for the callee to perform another external call, so this pattern is historically relied upon as an implicit reentrancy guard. In revive, "due to gas scale differences that guarantee does not automatically hold" — meaning the callee, converted to revive's gas/weight scale, may have enough real compute budget to reenter the caller. Because the match-arm ordering routes any non-zero-value call to `AllowReentry` (never `AllowNext`), the intended mitigation the `AllowNext` variant exists for is never applied to value transfers, regardless of gas amount.

### Impact Explanation
A callee contract invoked via a value transfer that the calling contract intentionally gas-capped at `CALL_STIPEND` to prevent reentrancy (mirroring the classic Solidity anti-reentrancy convention) is nonetheless granted full reentry permission (`AllowReentry`) rather than the restricted `AllowNext` semantics. This can allow a malicious callee to reenter the caller mid-transfer in scenarios where the caller's logic assumed reentrancy was impossible due to the gas stipend, which can lead to classic reentrancy exploitation (e.g., double-withdrawal / fund-theft patterns) in ported Solidity contracts relying on this convention within the pallet-revive EVM execution environment.

### Likelihood Explanation
This is fully attacker-controlled and reachable through the standard unprivileged contract execution path: any account can deploy/call an EVM contract on pallet-revive that issues a `CALL`/`STATICCALL` with attacker-chosen `value` and `gas_limit`. No privileged origin, governance, or node-level access is required — the malicious contract simply needs to be called with non-zero value and `gas_limit == 2300`. The condition is deterministic and trivially reproducible.

### Recommendation
Reorder/restructure the match so that the `gas_limit == CALL_STIPEND` heuristic is evaluated before/independent of the value-zero check, so that value-transferring calls capped at the stipend amount also receive `AllowNext` (or stronger) reentrancy protection, consistent with the documented intent of `ReentrancyProtection::AllowNext`. E.g.:
```
let (add_stipend, reentracy) = match gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND) {
    true => (true, ReentrancyProtection::AllowNext),
    false if !value.is_zero() => (true, ReentrancyProtection::AllowReentry),
    false => (false, ReentrancyProtection::AllowReentry),
};
```

### Proof of Concept
Rust integration test plan (in `substrate/frame/revive/src/exec/tests.rs` style, or EVM fixture test alongside `evm_call_stipends_work_for_transfer_zero`):
1. Deploy a `Caller` contract holding a balance, and a malicious `Reenterer` contract whose fallback/receive reenters `Caller` (e.g., calls a withdrawal function again).
2. From `Caller`, issue `Reenterer.call{value: v, gas: 2300}("")` where `v > 0`.
3. Instrument/log the `reentracy` value chosen in `run_call` (or directly assert via `MockStack`-style test using `ctx.ext.call` with `ReentrancyProtection` and asserting which variant is passed) to confirm `AllowReentry` is selected instead of `AllowNext`.
4. Have `Reenterer`'s fallback attempt a second call back into `Caller`'s withdrawal path; assert that the reentrant call **succeeds** (not rejected with `ReentranceDenied`) despite `gas_limit == CALL_STIPEND`, and that `Caller`'s final balance reflects a double-withdrawal rather than the expected single-transfer accounting.
5. Fuzz `(value, gas_limit)` pairs around 2300 with `value > 0` to confirm the `AllowNext` branch is never selected for any non-zero value, only for `value == 0`.

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

**File:** prdoc/stable2603/pr_11227.prdoc (L4-19)
```text
  description: "## Summary\n\nAdd tests that verify the `AllowNext` reentrancy path\
    \ is triggered for zero-value `transfer` and `send` calls.\n\n### How solc 0.8.30\
    \ handles the 2300 gas stipend\n\n| Solidity call | value | gas passed by compiler\
    \ | Stipend source |\n|---|---|---|---|\n| `target.transfer(amount)` | > 0 | `0`\
    \ | EVM adds 2300 automatically |\n| `target.send(amount)` | > 0 | `0` | EVM adds\
    \ 2300 automatically |\n| `target.transfer(0)` | 0 | `2300` | Compiler injects\
    \ explicitly |\n| `target.send(0)` | 0 | `2300` | Compiler injects explicitly\
    \ |\n| `target.call{value: v}(\"\")` | any | remaining gas | No stipend (forwards\
    \ all gas) |\n\nThe zero-value case is the one detected by our `gas_limit == CALL_STIPEND`\
    \ heuristic, which triggers `AllowNext`.\n\n## Changes\n\n- Add `testTransferZero`\
    \ / `testSendZero` to `Stipends.sol` fixture \u2014 these call `transfer(0)` and\
    \ `send(0)` on EOA, DoNothingReceiver, and SimpleReceiver\n- Add corresponding\
    \ Rust tests that exercise the `AllowNext` path\n- Add trace logs to the call\
    \ stipend match for debugging\n\n## Test plan\n\n- [x] `evm_call_stipends_work_for_transfer_zero`\
    \ passes, logs show `gas_limit=2300` \u2192 `AllowNext`\n- [x] `evm_call_stipends_work_for_send_zero`\
    \ passes, logs show `gas_limit=2300` \u2192 `AllowNext`"
```
