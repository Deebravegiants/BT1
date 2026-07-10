### Title
Detached Deposit-Refund Promises Permanently Lock Funds in the MPC Contract - (File: `crates/contract/src/lib.rs`)

### Summary

Three locations in the MPC contract schedule deposit refunds using `Promise::new(account).transfer(amount).detach()`. The `.detach()` call means the transfer receipt is fire-and-forget: if the transfer fails (e.g., the recipient contract account has been deleted between the call and receipt processing), the excess deposit is not returned to the caller and instead becomes permanently irrecoverable — either stuck in the MPC contract's balance or silently dropped — with no retry or withdrawal mechanism.

### Finding Description

The pattern appears in three production functions:

**1. `require_deposit` (called by `sign`, `request_app_private_key`, `verify_foreign_transaction`)** [1](#0-0) 

```rust
Some(diff) => {
    if diff > NearToken::from_yoctonear(0) {
        log!("refund excess deposit {diff} to {predecessor}");
        Promise::new(predecessor.clone()).transfer(diff).detach();
    }
}
```

**2. `submit_participant_info`** [2](#0-1) 

```rust
if let Some(diff) = attached.checked_sub(cost)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(account_id).transfer(diff).detach();
}
```

**3. `propose_update`** [3](#0-2) 

```rust
if let Some(diff) = attached.checked_sub(required)
    && diff > NearToken::from_yoctonear(0)
{
    Promise::new(proposer).transfer(diff).detach();
}
```

In all three cases, `.detach()` schedules the transfer in a new receipt but discards the result. The MPC contract never observes whether the transfer succeeded or failed. There is no fallback, no retry, and no on-chain withdrawal mechanism for the caller to reclaim the deposit if the transfer receipt fails.

In NEAR's async execution model, when a detached transfer receipt fails (e.g., the recipient account no longer exists), the NEAR runtime generates a refund receipt directed at the *predecessor of the failed receipt* — which is the MPC contract itself, not the original caller. The MPC contract's balance increases by the refund amount, but the contract has no code path to redistribute those funds. They are permanently locked.

### Impact Explanation

Any smart contract that:
1. Calls `sign()`, `request_app_private_key()`, `verify_foreign_transaction()`, `submit_participant_info()`, or `propose_update()` with an excess deposit, **and**
2. Is subsequently deleted (or has its account removed) before the refund receipt is processed

will permanently lose the excess deposit. The funds accumulate in the MPC contract's balance with no mechanism for recovery. For `propose_update`, the required deposit covers storage for a full contract binary upload, meaning the excess could be substantial (many NEAR tokens). For `sign`/`request_app_private_key`, any caller that over-attaches is at risk.

This matches **Medium** impact: balance and accounting invariants of the chain-signature contract are broken — the contract silently accumulates irrecoverable user funds — without requiring operator misconfiguration or network-level DoS.

### Likelihood Explanation

Smart contracts routinely call the MPC contract to request signatures (e.g., DeFi protocols, bridge relayers, wallet abstractions). These contracts are upgraded and replaced over time; the old contract account is deleted as part of the upgrade. If the old contract called `sign()` with excess deposit in its final transaction, the refund receipt will target a deleted account. The NEAR runtime's refund-on-failure path then credits the MPC contract, not the original caller. This is a realistic, non-adversarial scenario that requires no special privileges.

### Recommendation

Replace the fire-and-forget `.detach()` pattern with a checked promise chain, or implement a pull-based refund model:

**Option A – Checked promise (return the promise result):**
```rust
// Instead of:
Promise::new(predecessor.clone()).transfer(diff).detach();
// Use (and return the Promise so the SDK checks it):
return PromiseOrValue::Promise(Promise::new(predecessor.clone()).transfer(diff));
```

**Option B – Pull-based refund map:**
Store unclaimed refunds in a `LookupMap<AccountId, NearToken>` and expose a `claim_refund()` method, so callers can retrieve their deposit at any time regardless of account state at the time of the original call.

### Proof of Concept

1. Deploy a smart contract `caller.near` that calls `sign()` on the MPC contract attaching `1 NEAR` (excess above the 1 yoctoNEAR minimum).
2. The MPC contract's `require_deposit` computes `diff ≈ 1 NEAR` and schedules `Promise::new("caller.near").transfer(1 NEAR).detach()`.
3. In the same or next block, `caller.near` is deleted (e.g., via `DeleteAccount` action), transferring its remaining balance to a beneficiary.
4. The refund receipt targeting `caller.near` is processed; the account no longer exists; the receipt fails.
5. NEAR runtime generates a refund-on-failure receipt crediting the MPC contract (`v1.signer`) with `1 NEAR`.
6. The MPC contract's balance increases by `1 NEAR`, but no code path in the contract redistributes or tracks this amount.
7. The `1 NEAR` is permanently locked in the MPC contract. [4](#0-3) [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L843-848)
```rust
            // Refund the difference if the proposer attached more than required
            if let Some(diff) = attached.checked_sub(cost)
                && diff > NearToken::from_yoctonear(0)
            {
                Promise::new(account_id).transfer(diff).detach();
            }
```

**File:** crates/contract/src/lib.rs (L1298-1334)
```rust
    #[payable]
    #[handle_result]
    pub fn propose_update(
        &mut self,
        #[serializer(borsh)] args: ProposeUpdateArgs,
    ) -> Result<UpdateId, Error> {
        // Only voters can propose updates:
        let proposer = self.voter_or_panic();
        let update: Update = args.try_into()?;

        let attached = env::attached_deposit();
        let required = ProposedUpdates::required_deposit(&update);
        if attached < required {
            return Err(InvalidParameters::InsufficientDeposit {
                attached: attached.as_yoctonear(),
                required: required.as_yoctonear(),
            }
            .into());
        }

        let id = self.proposed_updates.propose(update);

        log!(
            "propose_update: signer={}, id={:?}",
            env::signer_account_id(),
            id,
        );

        // Refund the difference if the proposer attached more than required.
        if let Some(diff) = attached.checked_sub(required)
            && diff > NearToken::from_yoctonear(0)
        {
            Promise::new(proposer).transfer(diff).detach();
        }

        Ok(id)
    }
```
