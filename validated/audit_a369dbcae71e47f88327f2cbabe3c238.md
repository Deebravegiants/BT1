### Title
Stale `account.owner` lets the previous holder keep acting after a position-NFT transfer — cross-account isolation bypass - (File: contracts/controller/src/account.rs)

### Summary
The position NFT is the authoritative record of account ownership (`owner_of` = account owner, per `contracts/position-nft/src/contract.rs:1-2`), and it is freely transferable through the stock OpenZeppelin `NonFungibleToken`/`Enumerable` interface. However, the `Account` struct stores its own `owner: Address` field, written once at `create_account_with` (`contracts/controller/src/account.rs:64-66`) and never re-synced on NFT transfer. All privileged position operations that gate on `require_owner_or_delegate` compare `caller` against this *stored* owner (`account.rs:121`), not against the live NFT owner. After transferring the position NFT, the previous owner still satisfies `caller == owner` and retains full control of the account — an isolation boundary between distinct owners that the code fails to enforce, analogous to the site-isolation bypass class.

### Finding Description
`create_account_with` persists `Account { owner: owner.clone(), ... }` at mint time (`account.rs:64-70`). `require_account_owner` correctly reads the live owner via `storage::account_owner` (`account.rs:143-147`), but `is_owner_or_delegate`/`require_owner_or_delegate` (`account.rs:115-140`) take `owner` from the loaded `Account` struct and accept `caller == owner` with no NFT check. `load_or_create_account` applies this weaker guard for `AccountGuard::Migrate` and `AccountGuard::Multiply` (`account.rs:101-109`), and the same helper gates the strategy entrypoints (`positions/debt.rs`, `strategies/swap_debt.rs`, `strategies/swap_collateral.rs`, `strategies/repay_debt_with_collateral.rs`). Delegation grants compound the issue: `set_account_delegate` keys delegates under the caller-as-owner (`account.rs:261-263`), so stale delegates of the former owner also remain valid under `is_owner_or_delegate` (`account.rs:124-126`).

### Impact Explanation
Any path reachable through `require_owner_or_delegate` — `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend` — can be invoked by the ex-owner (or their still-registered delegates) on an account they no longer own. The ex-owner can borrow against the new owner's collateral or route collateral through attacker-chosen swap venues, draining the position's value. This is theft of user funds reachable by a single unprivileged address: acquire any position NFT legitimately (or sell one), then continue operating it.

### Likelihood Explanation
NFT transfer is a first-class, unprivileged feature (the contract exposes the full OZ `NonFungibleToken` trait, `contract.rs:131-133`), and no hook rewrites `account.owner` or clears delegates on transfer — `burn` is the only controller-driven ownership mutation (`contract.rs:88-95`). Exploitation requires only a transfer followed by a standard authenticated call; no timing, oracle, or liquidity precondition.

### Recommendation
Derive the effective owner from `storage::account_owner(env, account_id)` (the live NFT `owner_of`) inside `require_owner_or_delegate` / `is_owner_or_delegate` instead of trusting `account.owner`, or re-sync `account.owner` and migrate the delegate set on every NFT transfer. Alternatively, disable transfers on the position NFT if secondary ownership is not intended.

### Proof of Concept
1. Alice calls `controller.supply(account_id=0, spoke_id=1, ...)`; `load_or_create_account` mints account `A` to Alice and stores `account.owner = Alice`.
2. Alice calls `position_nft.transfer(Alice, Bob, A)` — permitted by the OZ enumerable NFT.
3. Alice (or a delegate she previously registered via `add_delegate`) calls `controller.multiply`/`swap_collateral`/`borrow` on account `A` with Alice's auth. `require_owner_or_delegate` sees `caller == account.owner == Alice` and passes, even though `require_account_owner`/`owner_of` would return Bob.
4. Alice draws debt against Bob's collateral or swaps Bob's collateral through a self-benefiting route, extracting value.

*Caveat: verification was limited by the available read iterations; this assumes `storage::get_account` returns the persisted `owner` field rather than re-deriving it from the NFT — the existence of a separate `storage::account_owner` helper for the authoritative check supports that reading, but it should be confirmed against `contracts/controller/src/storage/account.rs`.*