### Title
Unchecked `.detach()` on Refund Transfers Silently Traps Excess Deposits - (File: `crates/contract/src/lib.rs`)

### Summary

The NEAR MPC contract fires refund transfers via `Promise::new(...).transfer(diff).detach()` in three places without checking whether the transfer succeeded. If the recipient account cannot receive NEAR (e.g., a calling contract with no default/receive handler), the transfer silently fails and the excess deposit is permanently trapped in the MPC contract's balance. This is the direct NEAR analog of the unchecked `call` opcode return value in `LowLevelETH.sol`.

---

### Finding Description

In NEAR SDK, `.detach()` on a `Promise` means the promise is scheduled but its result is never observed — no callback is registered, no error is surfaced, and the calling transaction succeeds regardless of whether the transfer actually landed. This is semantically identical to the Solidity pattern of ignoring the boolean return value of a low-level `call`.

Three refund paths in `crates/contract/src/lib.rs` share this pattern:

**1. `require_deposit` (line 137)** — called from every user-facing request method (`sign`, `request_app_private_key`, `verify_foreign_transaction`):

```rust
fn require_deposit(minimum_deposit: NearToken, predecessor: &AccountId) {
    ...
    Some(diff) => {
        if diff > NearToken::from_yoctonear(0) {
            log!("refund excess deposit {diff} to {predecessor}");
            Promise::new(predecessor.clone()).transfer(diff).detach(); // ← unchecked
        }
    }
``` [1](#0-0) 

**2. `submit_participant_info` (line 847)** — refunds excess storage deposit to the node submitting attestation:

```rust
Promise::new(account_id).transfer(diff).detach(); // ← unchecked
``` [2](#0-1) 

**3. `propose_update` (line 1330)** — refunds excess deposit to the governance proposer:

```rust
Promise::new(proposer).transfer(diff).detach(); // ← unchecked
``` [3](#0-2) 

---

### Impact Explanation

When the recipient is a contract account that has no default function (the NEAR equivalent of no `fallback`/`receive`), the NEAR runtime rejects the transfer receipt. Because `.detach()` was used, this rejection is invisible to the MPC contract — the outer transaction succeeds, the excess deposit is debited from the caller, but the refund receipt fails and the tokens remain permanently in the MPC contract's own account balance. There is no sweep or recovery mechanism in the contract to reclaim these stranded funds.

This breaks the production accounting invariant that every excess deposit attached to a request is returned to its sender. The impact matches: **Medium — balance/accounting invariant broken without requiring operator misconfiguration or network-level DoS.**

---

### Likelihood Explanation

Any smart contract on NEAR that calls `sign()`, `request_app_private_key()`, `verify_foreign_transaction()`, `submit_participant_info()`, or `propose_update()` and attaches more than the minimum deposit is at risk. Contracts that act as intermediaries (e.g., DeFi protocols, DAO treasuries, automated bots) commonly lack a default function. The minimum deposit is only 1 yoctoNEAR, so any practical caller will attach more, making the excess-deposit path the common case rather than the exception.

---

### Recommendation

Replace each `.detach()` refund with a chained callback that panics (or logs and handles) on transfer failure, or use `#[handle_result]` to propagate the error. At minimum, the transfer promise should not be detached:

```rust
// Instead of:
Promise::new(predecessor.clone()).transfer(diff).detach();

// Use a checked pattern — chain a then-callback or return the promise:
return Promise::new(predecessor.clone()).transfer(diff);
// (and adjust the function signature to return PromiseOrValue<()>)
```

Alternatively, accumulate failed refunds in a storage map and expose a `claim_refund` method, mirroring the pull-payment pattern.

---

### Proof of Concept

1. Deploy a NEAR contract `Attacker` with **no default function**.
2. From `Attacker`, call `sign(request)` on the MPC contract attaching `2 yoctoNEAR` (minimum is `1 yoctoNEAR`).
3. `require_deposit` computes `diff = 1 yoctoNEAR` and fires `Promise::new(Attacker).transfer(1).detach()`.
4. The NEAR runtime schedules the transfer receipt. When it executes, `Attacker` has no default function, so the receipt fails.
5. Because `.detach()` was used, the MPC contract never sees the failure. The outer `sign` transaction succeeds.
6. The `1 yoctoNEAR` excess deposit is now permanently in the MPC contract's balance with no recovery path.
7. Repeat at scale: every contract-based caller loses its excess deposit silently. [4](#0-3) [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L344-357)
```rust
    #[payable]
    pub fn sign(&mut self, request: SignRequestArgs) {
        log!(
            "sign: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        let (domain_config, predecessor) = self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::Sign,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );
```

**File:** crates/contract/src/lib.rs (L844-848)
```rust
            if let Some(diff) = attached.checked_sub(cost)
                && diff > NearToken::from_yoctonear(0)
            {
                Promise::new(account_id).transfer(diff).detach();
            }
```

**File:** crates/contract/src/lib.rs (L1327-1331)
```rust
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }
```
