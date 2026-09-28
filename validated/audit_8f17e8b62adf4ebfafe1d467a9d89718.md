### Title
Stale `account.owner` lets a previous NFT holder retain spending authority over a transferred lending account - (File: contracts/controller/src/account.rs)

### Summary
The controller pins an account's owner to the `Address` stored in `Account.owner` at mint time, and every sensitive flow (`borrow`, `withdraw`, `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend`, liquidation `Credit` receiver) authorizes via `require_owner_or_delegate`, which compares `caller` against that stored field — not against the live position-NFT owner. The position NFT is freely transferable (`position-nft::transfer`/`transfer_from`), and no transfer hook rewrites `account.owner`. After an account NFT changes hands, the previous holder remains authorized to borrow and withdraw against the account, while the new NFT owner is rejected.

### Finding Description
`Account.owner` is set once in `create_account_with` when the NFT is minted (`contracts/controller/src/account.rs:64-65`). Authorization for value-moving entrypoints goes through `require_owner_or_delegate`, which returns true when `caller == owner` using the stored field (`contracts/controller/src/account.rs:115-140`). `load_or_create_account` applies this guard for `Migrate`/`Multiply` (`contracts/controller/src/account.rs:101-109`), and `debt.rs`/`supply.rs`/the swap-strategy files call the same helper for `borrow`, `withdraw`, `swap_debt`, `swap_collateral`, and `repay_debt_with_collateral`.

Only the account-lifecycle helpers `renew_account`, `add_delegate`, `remove_delegate` use `require_account_owner`, which reads the live NFT owner via `storage::account_owner` (`contracts/controller/src/account.rs:143-148`). So two different notions of "owner" exist: the live NFT holder and the stale stored `Address`.

The position NFT implements stock OpenZeppelin `transfer`/`transfer_from`; the declared invariant notes only that delegate grants from the previous owner go inactive (`scripts/permissionless_entrypoints.txt:111`). There is no evidence of a controller callback or storage update that rewrites `account.owner` or the delegate map keyed by the old owner (`storage::get_delegates(env, account_id, owner)` at `account.rs:126` is keyed by the stored owner too).

This is the same class as CVE-2026-45563: a parameter acting as an identity/authorization token (`account_id` → stored `owner`) is trusted without re-checking it against the actual current owner.

### Impact Explanation
Theft of user funds. An attacker who sells or transfers an account NFT — e.g., via an OTC sale of an account holding supplied collateral — retains full `require_owner_or_delegate` authority. They can then call `withdraw` to pull the collateral the buyer paid for, or `borrow` to max out the account's LTV and leave the buyer holding bad debt. The buyer, despite owning the NFT, cannot call any owner/delegate-gated flow. Both directions are broken: ex-owner keeps spending power; new owner is locked out of `borrow`/`withdraw`/delegation management.

### Likelihood Explanation
Any unprivileged address can execute this: transfer the NFT (or have a buyer receive it), then immediately call `controller::withdraw`/`borrow` as the now-stale `account.owner`. No privileged role, no timing constraint, no oracle manipulation. The only precondition is that the account holds collateral — which is precisely what makes a transferred account valuable.

Caveat: I was unable to confirm within the available context whether `position-nft` transfer performs any cross-contract call back into the controller to update `account.owner`. The evidence I found — the invariant file discussing only delegate inactivation, and `require_account_owner` existing precisely because the stored field can diverge from `owner_of` — indicates it does not, but a transfer hook would invalidate this finding.

### Recommendation
On every `require_owner_or_delegate`/`is_owner_or_delegate` call, resolve the owner from `storage::account_owner` (live NFT `owner_of`) instead of the stored `account.owner` field, and key `get_delegates` by that resolved owner. Alternatively, add a transfer hook so the controller updates `account.owner` and clears delegates whenever the NFT moves. Add a test: owner supplies, transfers NFT, assert previous owner's `withdraw` reverts and new owner's succeeds.

### Proof of Concept
1. Alice calls `controller::supply` (account_id = 0) to create account A with collateral; `account.owner = alice`.
2. Alice calls `position-nft::transfer(alice, bob, A)`. NFT `owner_of(A)` is now bob; `account.owner` remains alice.
3. Alice calls `controller::withdraw(alice, A, spoke_id, [...])`. `require_owner_or_delegate` sees `caller == account.owner` and authorizes.
4. Collateral leaves to alice; bob owns an emptied account. Alternatively alice calls `borrow` to draw debt against bob's collateral before withdrawing.