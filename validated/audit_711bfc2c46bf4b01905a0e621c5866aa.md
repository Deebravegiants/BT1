### Title
Value-transfer `CALL`s always get `ReentrancyProtection::AllowReentry`, defeating the stipend-based anti-reentrancy heuristic - (File: substrate/frame/revive/src/vm/evm/instructions/contract.rs)

### Summary
In `run_call`, the match that decides `add_stipend`/`ReentrancyProtection` places `(false, _) => (true, ReentrancyProtection::AllowReentry)` before the stipend-heuristic arm `(_, true) => (true, ReentrancyProtection::AllowNext)`. Because Rust match arms are evaluated in order and `false` (i.e. `value.is_zero() == false`) is matched via a wildcard on the second tuple element, **every** value-carrying `CALL` — including the canonical Solidity `.transfer()`/`.send()` pattern that passes exactly `gas_limit == CALL_STIPEND (2300)` — takes the `AllowReentry` branch instead of the intended `AllowNext` protection. The gas-stipend heuristic can therefore never fire for the exact call shape (`value != 0`, `gas == 2300`) it was written to protect.

### Finding Description
`run_call` at [1](#0-0)  computes:

```rust
let (add_stipend, reentracy) =
    match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND))
    {
        (false, _) => (true, ReentrancyProtection::AllowReentry),
        (_, true) => (true, ReentrancyProtection::AllowNext),
        (_, _) => (false, ReentrancyProtection::AllowReentry),
    };
```

Match arms are tested top-to-bottom. `(false, _)` matches whenever `value.is_zero()` is `false` — i.e. whenever the call transfers nonzero value — irrespective of `gas_limit`. Since Solidity's `.transfer()`/`.send()` idiom compiles to exactly this shape (`value != 0`, `gas_limit == 2300`), the second arm `(_, true) => AllowNext`, which is the code's actual anti-reentrancy heuristic for the stipend case, is unreachable for the very call pattern the accompanying comment claims to detect ("For zero-value transfer/send, solc injects gas_limit = 2300" — this description is itself backwards, since Solidity `.transfer()`/`.send()` always carry nonzero value).

The practical consequence: `interpreter.ext.call(&CallResources::from_ethereum_gas(gas_limit, add_stipend=true), &callee, value, input, ReentrancyProtection::AllowReentry, ...)` at [2](#0-1)  is invoked with full reentrancy permission for every nonzero-value call, regardless of whether the caller intended a stipend-limited, non-reentrant send. There is no code path by which an attacker (or a normal contract author using the standard `.transfer()` pattern) can obtain `AllowNext` protection on a value-bearing call — the branch ordering makes it structurally dead for that case.

This is reachable purely through normal, unprivileged contract execution: any signed account can deploy a "victim" contract using `payable(addr).transfer(amount)` (compiled to CALL with `value != 0`, `gas_limit == 2300`) and a malicious receiving contract with a fallback that calls back into the victim. Because `AllowReentry` (not `AllowNext`) is what actually gets passed to `interpreter.ext.call`, the runtime's reentrancy gate does not restrict the reentrant call, unlike what the stipend-gas convention is meant to guarantee.

### Impact Explanation
If a victim contract relies on the classic `.transfer()`/`.send()` gas-stipend convention to prevent reentrancy (a widely used real-world pattern, and the exact pattern the engine's own heuristic claims to special-case), the runtime's reentrancy safeguard is silently bypassed for all such calls. A malicious receiving contract's fallback can reenter the victim contract during the value transfer and perform additional withdrawals/state mutations before the victim's accounting is finalized, enabling double-spend/fund-draining reentrancy attacks — the same class of bug as the historical DAO hack — despite the caller's use of the gas-stipend idiom that is supposed to be defended against exactly this.

### Likelihood Explanation
Fully triggerable by any unprivileged user: deploy two contracts (victim using `.transfer()`/`.send()`, attacker with a reentrant fallback), call the victim via a normal extrinsic. No privileged origin, governance, or admin action required. The condition (`value != 0`, `gas_limit == CALL_STIPEND`) is the default, idiomatic Solidity output for `.transfer()`/`.send()`, so this is not a contrived edge case — it is the common path, making it highly likely to affect real contracts deployed on this pallet.

### Recommendation
Reorder the match so the stipend-heuristic check is evaluated before the blanket nonzero-value case, e.g.:
```rust
let (add_stipend, reentracy) = match (value.is_zero(), gas_limit.try_into().is_ok_and(|limit: u64| limit == CALL_STIPEND)) {
    (_, true) => (true, ReentrancyProtection::AllowNext),
    (false, _) => (true, ReentrancyProtection::AllowReentry),
    (_, _) => (false, ReentrancyProtection::AllowReentry),
};
```
so that any call with `gas_limit == CALL_STIPEND` (value zero or nonzero) receives `AllowNext`, matching the documented intent, and only genuinely unrestricted-gas value transfers receive `AllowReentry`.

### Proof of Concept
Rust integration test in `substrate/frame/revive/src/exec/tests.rs` (or an EVM-instruction-level test in `vm/evm`):
1. Deploy `Victim` contract holding a balance, with a withdraw function that does `checks-then-`.transfer(amount)`-then-effects` (i.e., relies on stipend semantics for reentrancy safety) to `msg.sender`.
2. Deploy `Attacker` contract whose `receive()`/fallback calls back into `Victim.withdraw()` before the victim updates its internal balance ledger.
3. Fund `Victim`, have `Attacker` call `Victim.withdraw()` via a normal extrinsic.
4. Assert that `Victim`'s recorded balance decreases by exactly one legitimate withdrawal amount, but its actual on-chain balance decreases by N × amount (N = number of reentrant calls achieved during the fallback), proving reentrancy occurred despite the `.transfer()` stipend idiom.
5. Additionally unit-test `run_call`'s match directly: assert that for `value != 0 && gas_limit == CALL_STIPEND`, the returned reentrancy mode is `AllowNext`, not `AllowReentry` — this assertion currently fails against the code as written.

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
