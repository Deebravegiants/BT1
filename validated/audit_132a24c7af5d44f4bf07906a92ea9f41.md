### Title
Unchecked Detached Transfer Promise Silently Loses Excess Deposit Refunds - (File: `crates/contract/src/lib.rs`)

### Summary

The `require_deposit` helper in `crates/contract/src/lib.rs` refunds excess attached deposits to callers of `sign()`, `request_app_private_key()`, and `verify_foreign_transaction()` using `Promise::transfer().detach()`. The `.detach()` call explicitly discards the promise result, so any failure of the refund transfer is silently swallowed — the contract retains the excess deposit with no error surfaced to the caller.

### Finding Description

`require_deposit` is called by every user-facing request entry point to enforce a minimum deposit and refund any overpayment: [1](#0-0) 

The refund path at line 137 is:

```rust
Promise::new(predecessor.clone()).transfer(diff).detach();
```

`.detach()` severs the promise from the current execution context. NEAR's SDK will schedule the transfer receipt, but the outcome — success or failure — is never observed by the contract. If the transfer receipt fails for any reason (e.g., the predecessor account is deleted between the call and the receipt execution, or the contract's own balance is unexpectedly insufficient due to concurrent state changes), the failure is silently dropped. The contract keeps the excess deposit and the caller receives no refund and no error.

This is the direct NEAR analog of the M-08 pattern: an external value-transfer whose return value is not validated, allowing silent fund retention on failure.

### Impact Explanation

Any caller of `sign()`, `request_app_private_key()`, or `verify_foreign_transaction()` who attaches more than the 1 yoctoNEAR minimum deposit may permanently lose the excess. The contract's accounting invariant — "excess deposits are always returned to the caller" — is broken without any on-chain signal. The lost funds remain locked in the contract with no recovery path. [2](#0-1) 

This maps to the **Medium** allowed impact: balance/accounting invariant breakage that does not require operator misconfiguration or network-level DoS.

### Likelihood Explanation

The failure scenario requires the predecessor's account to be unreachable at receipt execution time (e.g., account deleted in the same block) or the contract balance to be insufficient. Both are rare under normal operation, but the window is real: NEAR receipts execute asynchronously, and account deletion is a valid on-chain operation. An adversarial caller could deliberately delete their account after submitting the call to trigger the silent loss (griefing themselves or testing the path). More practically, any future contract upgrade that alters balance accounting could expose this silently.

### Recommendation

Replace the detached transfer with a checked pattern. Either:

1. Return the transfer promise so the caller's transaction fails if the refund fails:
   ```rust
   // Instead of .detach(), return the promise
   Promise::new(predecessor.clone()).transfer(diff)
   ```
   (requires the calling function to propagate the `Promise` return type)

2. Or use `#[callback_result]` on a small callback that logs or panics on refund failure, mirroring the pattern already used for `fail_on_timeout` in `return_ck_and_clean_state_on_success`: [3](#0-2) 

The simplest fix consistent with the existing codebase style is to not call `.detach()` and instead propagate the refund promise as the return value of `require_deposit`, letting the NEAR runtime surface any failure to the caller.

### Proof of Concept

1. Caller submits `sign()` with 1 NEAR attached (excess = 1 NEAR − 1 yoctoNEAR).
2. `require_deposit` computes `diff = 1 NEAR − 1 yoctoNEAR` and schedules `Promise::new(predecessor).transfer(diff).detach()`.
3. Before the transfer receipt executes, the predecessor account is deleted (valid NEAR operation).
4. The transfer receipt fails; NEAR drops it silently because the promise was detached.
5. The contract retains the ~1 NEAR excess. The caller's `sign()` call succeeds (the yield is queued normally), but the refund is permanently lost with no error emitted. [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L122-141)
```rust
fn require_deposit(minimum_deposit: NearToken, predecessor: &AccountId) {
    let deposit = env::attached_deposit();
    match deposit.checked_sub(minimum_deposit) {
        None => {
            env::panic_str(
                &InvalidParameters::InsufficientDeposit {
                    attached: deposit.as_yoctonear(),
                    required: minimum_deposit.as_yoctonear(),
                }
                .to_string(),
            );
        }
        Some(diff) => {
            if diff > NearToken::from_yoctonear(0) {
                log!("refund excess deposit {diff} to {predecessor}");
                Promise::new(predecessor.clone()).transfer(diff).detach();
            }
        }
    }
}
```

**File:** crates/contract/src/lib.rs (L2295-2303)
```rust
                let fail_on_timeout_gas = Gas::from_tgas(self.config.fail_on_timeout_tera_gas);
                let promise = Promise::new(env::current_account_id()).function_call(
                    method_names::FAIL_ON_TIMEOUT.to_string(),
                    vec![],
                    NearToken::from_near(0),
                    fail_on_timeout_gas,
                );
                near_sdk::PromiseOrValue::Promise(promise.as_return())
            }
```
