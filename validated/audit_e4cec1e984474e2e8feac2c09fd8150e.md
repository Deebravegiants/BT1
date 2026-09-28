### Title
Stale position-NFT approval remains valid after ownership transfer - (File: `contracts/position-nft/src/lib.rs`)

### Summary
The position NFT clears ownership on transfer but does not invalidate the token-level approval recorded by `approve`. A previously approved address can therefore retain authority over the NFT after it changes hands and use `transfer_from` to take the position from the new owner.

### Finding Description
`approve` persists spender authorization for a `token_id`, which is also the lending `account_id`. The transfer path updates the token owner but leaves the existing approval entry associated with that `token_id` intact instead of treating the approval as owner-scoped state that must be invalidated.

Because `transfer_from` authorizes the operator from the still-present approval record, the old approved spender can submit a transfer for the NFT after the original owner has sold, gifted, or otherwise transferred it. The controller resolves account control from position-NFT ownership, so the attacker who takes the NFT can then act as the account owner through owner-authorized controller calls such as `withdraw` [1](#0-0) .

This is the local analogue of failing to invalidate stale translation/context entries after updating them: the owner entry changes, but the derived authorization entry remains usable.

### Impact Explanation
An attacker can steal an account NFT and every economically accessible right attached to it. For an account holding withdrawable collateral, the attacker can call `withdraw` and take the collateral to their own address. For accounts whose collateral cannot currently be withdrawn, the attacker can permanently freeze the position by moving the NFT to an uncontrolled address.

This constitutes theft of user funds and, where debt prevents withdrawal, permanent freezing of user funds.

### Likelihood Explanation
The exploit requires the victim to approve the attacker or a compromised approval recipient before transferring the NFT. Token approvals are a routine marketplace, automation, and integration pattern, and users reasonably expect approval to end when ownership changes.

All required actions are available to ordinary addresses:

1. The victim authorizes a spender with `approve`.
2. The victim transfers the NFT to another address.
3. The previously approved spender invokes `transfer_from` using the stale approval.
4. The spender becomes the account owner and calls owner-authorized controller entrypoints such as `withdraw`.

No privileged role, leaked key, oracle manipulation, or third-party service failure is required.

### Recommendation
Invalidate token-level approval whenever NFT ownership changes.

At minimum:

- Delete the `token_id` approval entry in both `transfer` and `transfer_from` after checking the caller's authorization.
- Ensure approval is scoped to the owner that granted it, not merely to the immutable token ID.
- Add regression coverage proving that `approve -> transfer -> transfer_from` fails for the previously approved spender.
- Also verify that changing ownership clears any pending approval TTL or authorization metadata that could otherwise be reused by the next owner.

### Proof of Concept
Assume Alice owns position NFT `token_id = 7`, which controls lending `account_id = 7` and its collateral.

1. Alice calls `approve` on the position NFT, approving Mallory for `token_id = 7`.
2. Alice sells or transfers the NFT to Bob by calling `transfer(from = Alice, to = Bob, token_id = 7)`.
3. The NFT owner is now Bob, but Mallory's approval record for `token_id = 7` remains.
4. Mallory calls `transfer_from(operator = Mallory, from = Bob, to = Mallory, token_id = 7)`.
5. The stale approval authorizes the transfer even though Alice—not Bob—granted it.
6. Mallory now controls `account_id = 7` and calls `withdraw(caller = Mallory, account_id = 7, withdrawals = [...], to = Some(Mallory))` to remove withdrawable collateral [2](#0-1) .

The decisive invariant violation is that the old approval remains usable after the ownership transition it was supposed to be bound to.

### Citations

**File:** contracts/controller/src/lib.rs (L117-128)
```rust
    /// Withdraws collateral to `to` or the caller and returns actual amounts in
    /// asset units. Zero withdraws an asset's full position. Requires owner or
    /// delegate authorization and post-withdrawal solvency.
    fn withdraw(
        env: Env,
        caller: Address,
        account_id: u64,
        withdrawals: Vec<(HubAssetKey, i128)>,
        to: Option<Address>,
    ) -> Vec<(HubAssetKey, i128)> {
        positions::process_withdraw(&env, &caller, account_id, &withdrawals, to)
    }
```
