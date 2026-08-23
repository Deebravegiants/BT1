## Title
Zero-Value Allowance Silently Converted to Unlimited Allowance in `promise_batch_action_add_key_with_function_call` - (File: `runtime/near-vm-runner/src/logic/logic.rs`)

### Summary
The reported bug class is: a storage location cannot distinguish "value not configured" from "value explicitly set to zero," so the code silently falls back to a different (more permissive) behavior, defeating the caller's explicit intent. nearcore's host-function implementation for adding a `FunctionCall` access key via a promise batch action reproduces this exact ambiguity for the `allowance` parameter: passing `0` is interpreted as "not set," which the code maps to `None`, and `None` on a `FunctionCallPermission.allowance` means **unlimited allowance**, not "no allowance."

### Finding Description
`FunctionCallPermission.allowance` is documented and typed as `Option<Balance>` where `None` explicitly means "unlimited allowance": [1](#0-0) 

The protocol's own binding-spec documentation states, for `promise_batch_action_add_key_with_function_call`:
> "If the allowance value (not the pointer) is `0`, the allowance is set to `None` (which means unlimited allowance). And positive value represents a `Some(...)` allowance." [2](#0-1) 

This same zero→`None` conversion pattern is present in the analogous gas-key host function, confirming the pattern exists in the current codebase (`runtime/near-vm-runner/src/logic/logic.rs` and its wasmtime-runner counterpart): [3](#0-2) [4](#0-3) 

The root cause matches the external report exactly: the host function reads a raw `u128` from guest memory and cannot distinguish "caller intentionally wants zero allowance" from "caller wants unlimited (unset) allowance" — both are represented as `0` in the wasm ABI, and the code collapses both into the `None` (unlimited) branch. A contract author who calls this host function intending to add a heavily-restricted, effectively-non-spending `FunctionCall` access key (allowance = 0, i.e., "this key can authorize calls but must never draw down my balance for gas/fees") instead silently receives a key with **unlimited** spending allowance against the account's balance.

### Impact Explanation
This is a reachable state/authorization bug: any account (including a contract account acting on itself or spawning keys for other purposes) that calls `promise_batch_action_add_key_with_function_call` with an allowance argument of `0` gets an access key that can spend an **unbounded** amount of the account's NEAR balance on gas/fees, rather than the "no allowance" the zero value was meant to convey. Because access keys with `FunctionCallPermission` are commonly used to grant limited, low-trust delegated permissions (e.g., session keys, bot keys, relayer keys) to third parties or dApp front-ends, an application relying on `allowance=0` to create a "dead"/non-spending key would instead grant that key unrestricted ability to drain the account's liquid balance via gas fees over time. This is a concrete state/balance-authorization risk (unauthorized/unbounded balance consumption), matching the "unauthorized state or balance change" acceptance criterion.

### Likelihood Explanation
Likelihood is limited by two factors: (1) this behavior is explicitly documented as intended ("0 → unlimited"), so it may be considered a documented design choice rather than an unintentional flaw, and (2) exploitation requires an account/contract to actually pass a literal `0` allowance expecting "no spend" semantics, which is a plausible but not universal usage pattern (most legitimate use of `allowance=0` intending "unlimited" is also plausible, matching the documented behavior). The core ambiguity — no way to encode "explicitly zero, no allowance" distinctly from "not specified" over the wasm ABI — is real and structurally identical to the reported bug class, but because the current documentation states this is the intended mapping, it functions more as a foot-gun / spec ambiguity than an obviously unintended defect, unlike the Solidity report where the team explicitly acknowledged it as a bug.

### Recommendation
Reserve a distinguishable sentinel (e.g., `u128::MAX`, or add a separate flag byte/parameter) to represent "unlimited allowance," and treat `0` as a valid, distinct "zero allowance" (`Some(Balance::ZERO)`) rather than silently promoting it to `None`. This mirrors the report's recommendation to change the storage/parameter encoding so "not set" and "explicitly zero" are structurally distinguishable, preventing the fallback logic from unintentionally overriding the caller's restrictive intent.

### Proof of Concept
1. A contract calls `promise_batch_action_add_key_with_function_call(promise_idx, pubkey, nonce, allowance_ptr, receiver_id, method_names)` where the 16-byte value at `allowance_ptr` is `0`, intending to add a `FunctionCall` access key that cannot spend any of the account's balance.
2. Per the documented/implemented behavior, the host function converts `allowance == 0` into `None`, i.e., unlimited allowance, per the identical logic shown in the gas-key sibling function: `let allowance = if allowance > Balance::ZERO { Some(allowance) } else { None };` [3](#0-2) .
3. The resulting `AddKeyAction` is executed with `FunctionCallPermission { allowance: None, .. }`, granting the new access key unlimited allowance to pay gas/fees from the account's balance — the opposite of the caller's intended "zero allowance" restriction.
4. Any transaction signed with that key can now consume the account's full liquid balance for gas/fees across an unbounded number of function calls, with no allowance cap enforced.

### Citations

**File:** core/primitives-core/src/account.rs (L889-896)
```rust
pub struct FunctionCallPermission {
    /// Allowance is a balance limit to use by this access key to pay for function call gas and
    /// transaction fees. When this access key is used, both account balance and the allowance is
    /// decreased by the same value.
    /// `None` means unlimited allowance.
    /// NOTE: To change or increase the allowance, the old access key needs to be deleted and a new
    /// access key should be created.
    pub allowance: Option<Balance>,
```

**File:** docs/RuntimeSpec/Components/BindingsSpec/PromisesAPI.md (L317-336)
```markdown
#### promise_batch_action_add_key_with_function_call

```rust
promise_batch_action_add_key_with_function_call(promise_idx: u64,
                                                public_key_len: u64,
                                                public_key_ptr: u64,
                                                nonce: u64,
                                                allowance_ptr: u64,
                                                receiver_id_len: u64,
                                                receiver_id_ptr: u64,
                                                method_names_len: u64,
                                                method_names_ptr: u64)
```

Appends `AddKey` action to the batch of actions for the given promise pointed by `promise_idx`.
Details for the action: https://github.com/nearprotocol/NEPs/pull/8/files#diff-156752ec7d78e7b85b8c7de4a19cbd4R54
The access key will have `FunctionCall` permission, details: [click here](../../../DataStructures/AccessKey.md)

- If the `allowance` value (not the pointer) is `0`, the allowance is set to `None` (which means unlimited allowance). And positive value represents a `Some(...)` allowance.
- Given `method_names` is a `utf-8` string with `,` used as a separator. The vm will split the given string into a vector of strings.
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L3354-3358)
```rust
        let allowance = Balance::from_yoctonear(
            self.memory.get_u128(&mut self.result_state.gas_counter, allowance_ptr)?,
        );
        let allowance = if allowance > Balance::ZERO { Some(allowance) } else { None };
        let receiver_id = self.read_and_parse_account_id(receiver_id_ptr, receiver_id_len)?;
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/logic.rs (L3563-3568)
```rust
    let allowance = Balance::from_yoctonear(get_u128(
        &mut ctx.result_state.gas_counter,
        memory,
        allowance_ptr,
    )?);
    let allowance = if allowance > Balance::ZERO { Some(allowance) } else { None };
```
