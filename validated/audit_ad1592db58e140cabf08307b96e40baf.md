### Title
Excess Deposit Refunded to Intermediary Contract Instead of Original Caller — (`File: crates/contract/src/lib.rs`)

---

### Summary

When `sign`, `request_app_private_key`, or `verify_foreign_transaction` is invoked through an intermediary NEAR contract (e.g., a bridge adapter, DeFi protocol, or any wrapper contract), any excess deposit above the 1 yoctoNEAR minimum is refunded to `predecessor_account_id()` — the intermediary contract — rather than to the original user who funded the call. The funds are permanently stranded in the intermediary contract unless it has an explicit withdrawal path.

---

### Finding Description

`check_request_preconditions` captures the refund target as `env::predecessor_account_id()` and passes it directly to `require_deposit`:

```rust
// crates/contract/src/lib.rs:295-296
let predecessor = env::predecessor_account_id();
require_deposit(minimum_deposit, &predecessor);
```

Inside `require_deposit`, any excess above the minimum is transferred to that same `predecessor`:

```rust
// crates/contract/src/lib.rs:134-138
Some(diff) => {
    if diff > NearToken::from_yoctonear(0) {
        log!("refund excess deposit {diff} to {predecessor}");
        Promise::new(predecessor.clone()).transfer(diff).detach();
    }
}
```

In a direct call (`User → MpcContract`), `predecessor_account_id()` is the user, so the refund is correct. But in a cross-contract call (`User → BridgeContract → MpcContract`), `predecessor_account_id()` is `BridgeContract`, not the user. The excess deposit is therefore sent to `BridgeContract`, not to the user who attached the funds.

This is structurally identical to M-07: in that report, excess `quoteTokens` were sent to `msg.sender` (the Market contract) instead of the reallocator who initiated the flow. Here, excess NEAR deposit is sent to the intermediary contract instead of the user who funded it.

All three user-facing payable entry points share this flaw through the shared `check_request_preconditions` helper:
- `sign` (line 352)
- `request_app_private_key` (line 477)
- `verify_foreign_transaction` (line 526)

---

### Impact Explanation

**Medium.** Any excess deposit attached by a user calling through an intermediary contract is permanently transferred to that intermediary contract. If the intermediary has no withdrawal function for arbitrary NEAR balances (which is the common case for purpose-built bridge or DeFi adapters), the funds are irrecoverable. This breaks the documented invariant that "any excess deposit is automatically refunded" — the refund goes to the wrong account. This is a direct, concrete loss of user funds without requiring any privileged access or network-level attack.

---

### Likelihood Explanation

NEAR's cross-contract call model is a first-class feature and is widely used by bridge protocols, DeFi aggregators, and intent-settlement layers — all of which are natural consumers of Chain Signatures. As the ecosystem grows, wrapper contracts calling `sign` on behalf of users become increasingly common. A user who attaches even a small excess (e.g., 1 milliNEAR instead of 1 yoctoNEAR) through such a wrapper loses that excess permanently. The minimum deposit is 1 yoctoNEAR, so any deposit above that triggers the vulnerable refund path.

---

### Recommendation

Refund the excess to `env::signer_account_id()` rather than `env::predecessor_account_id()`. In NEAR, `signer_account_id()` is always the original transaction signer (the human user), regardless of how many contract hops the call traverses. This ensures the refund reaches the party who actually funded the deposit:

```rust
// In require_deposit or check_request_preconditions:
let refund_target = env::signer_account_id(); // not predecessor_account_id()
Promise::new(refund_target).transfer(diff).detach();
```

Alternatively, accept an explicit `refund_to: Option<AccountId>` parameter in the request args so callers can specify the correct refund destination.

---

### Proof of Concept

1. Deploy an intermediary contract `bridge.near` that calls `mpc.near`'s `sign` method and forwards the user's attached deposit.
2. User calls `bridge.near` with 1 NEAR attached (intending to cover the 1 yoctoNEAR minimum with a safety margin).
3. `bridge.near` calls `mpc.near.sign(...)` forwarding the 1 NEAR deposit.
4. Inside `check_request_preconditions`:
   - `env::predecessor_account_id()` = `bridge.near`
   - `env::signer_account_id()` = `user.near`
5. `require_deposit` computes `diff = 1 NEAR - 1 yoctoNEAR ≈ 1 NEAR` and executes:
   ```rust
   Promise::new("bridge.near").transfer(diff).detach();
   ```
6. The user loses ~1 NEAR. `bridge.near` receives it with no mechanism to return it.

Relevant lines: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L294-296)
```rust
        // 3. Require the minimum deposit and refund any excess.
        let predecessor = env::predecessor_account_id();
        require_deposit(minimum_deposit, &predecessor);
```

**File:** crates/contract/src/lib.rs (L352-357)
```rust
        let (domain_config, predecessor) = self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::Sign,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );
```

**File:** crates/contract/src/lib.rs (L477-482)
```rust
        let (_, predecessor) = self.check_request_preconditions(
            domain_id,
            DomainPurpose::CKD,
            Gas::from_tgas(self.config.ckd_call_gas_attachment_requirement_tera_gas),
            MINIMUM_CKD_REQUEST_DEPOSIT,
        );
```

**File:** crates/contract/src/lib.rs (L526-531)
```rust
        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );
```
