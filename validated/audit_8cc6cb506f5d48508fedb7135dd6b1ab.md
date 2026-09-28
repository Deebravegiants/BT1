### Title
Stale delegate grant revives after NFT transfer round-trip, letting a reactivated delegate drain collateral (`contracts/controller/src/storage/account.rs`)

### Summary
CVE-2021-47506 is a bookkeeping race: an object is added to a tracking list (`del_recall_lru`), logically freed, but never removed from the list, so a later pass uses a dangling entry. The structural analog in XOXNO Lending is the `ControllerKey::Delegates(account_id)` grant: ownership transfer logically invalidates the grant (it is stamped `granted_by` with the old owner) but the entry is never deleted, so it silently becomes live again if the position NFT ever returns to the original owner.

### Finding Description
`get_delegates` loads the stored `DelegateGrant` and returns its delegate list only when `grant.granted_by == owner` (`contracts/controller/src/storage/account.rs:176-181`). Nothing clears the `Delegates` key on NFT transfer — `remove_account_entry` only runs when an account is deleted, not on transfer (`storage/account.rs:249-256`). The code itself acknowledges the resurrection hazard: `remove_delegate` deletes a stale grant precisely "preventing those grants from reactivating if the NFT returns to their original owner" (`storage/account.rs:223-238`). But that cleanup only runs if someone calls `revoke_delegate` while the grant is stale. If the NFT moves `A → B → A` with no revocation in between, `granted_by == A` again, and every delegate originally approved by `A` is live with no fresh consent.

Attack path: owner `A` grants `D` as delegate, then transfers the position NFT (sale, gift, or even a compromised-then-recovered key flow). `D` waits; the new holder `B` later sells/transfers the NFT back to `A` — a routine user action (`position-nft transfer` is a normal unprivileged entrypoint). `D`'s grant is now active again even though `A` reasonably believed delegation died with the transfer. `D` then invokes delegate-authorized position verbs (`require_owner_or_delegate` is checked across `positions/supply.rs`, `positions/debt.rs`, and the `swap_collateral`/`swap_debt`/`repay_debt_with_collateral` strategies) to manipulate `A`'s account — e.g., routing `A`'s collateral through a self-controlled swap venue to extract value.

### Impact Explanation
Theft of user funds / loss of collateral: a delegate who was implicitly revoked by the ownership change regains the ability to run collateral-moving operations on the victim's account, including routing collateral through unallowlisted swap venues where the attacker controls the counterparty.

### Likelihood Explanation
Medium: requires a prior delegation, an NFT transfer away, and a transfer back — all normal unprivileged user flows, but the victim's own actions are needed for the round-trip. No timing race is required; the stale entry persists indefinitely in storage until explicitly revoked or the account is deleted.

### Recommendation
Treat `Delegates` like other ownership-scoped state: either hook NFT-transfer observation to clear the `DelegateGrant`, or stamp the grant with a monotonically increasing ownership epoch/token generation (e.g., store the NFT transfer count or burn-generation in `DelegateGrant` and compare it in `get_delegates`), so a transfer permanently invalidates the entry even when it is never touched.

### Proof of Concept
1. `A` owns account `id` and calls the delegate-grant entrypoint approving `D`. `DelegateGrant{granted_by: A, delegates: [D]}` is written (`storage/account.rs:203-221`).
2. `A` calls position-nft `transfer` to `B`. The `Delegates` key is untouched — only `get_delegates`'s `granted_by` filter makes it inert (`storage/account.rs:176-181`).
3. `B` later transfers the NFT back to `A` (e.g., resale). `try_account_owner` now returns `A`, so `get_delegates` returns `[D]` again with no new grant.
4. `D` calls a delegate-authorized strategy such as `swap_collateral` naming a malicious route, extracting `A`'s collateral value — delegation `A` never re-consented to.

Note: I verified the grant-invalidation/revival mechanism in `storage/account.rs`, but could not fully enumerate which delegate-authorized verbs allow direct value extraction (delegate reach is visible in `positions/debt.rs` and `strategies/swap_collateral.rs` via `require_owner_or_delegate`, but each verb's payout semantics were not fully read). If delegates turn out to be restricted to operations that can only ever credit the account owner, the practical impact degrades to griefing rather than theft.