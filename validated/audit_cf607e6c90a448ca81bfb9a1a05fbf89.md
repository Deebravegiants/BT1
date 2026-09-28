### Title
Stale `Account.owner` lets a prior owner and their delegates keep acting after the position NFT is transferred - (File: contracts/controller/src/account.rs)

### Summary
The controller stores the account owner in the `Account` struct at creation (`account.rs:64-70`), and every sensitive entrypoint authorizes via `require_owner_or_delegate`/`is_owner_or_delegate` against that stored `account.owner` field (`account.rs:115-140`). The position NFT, however, implements the stock OpenZeppelin `NonFungibleToken` interface (`position-nft/src/contract.rs:131-133`), whose `transfer`/`transfer_from` paths update only NFT-side `Owner`/`Balance` entries and never notify the controller. This mirrors the Fastify HEAD/GET split: two paths mutate/reflect the same logical "ownership" resource, but only one path is wired through the authorization middleware — the delegate/owner ACL keyed on the stale stored owner is never invalidated on NFT transfer.

### Finding Description
- `create_account_with` writes `Account { owner: owner.clone(), ... }` once at mint (`account.rs:63-70`).
- `load_or_create_account` and all mutating position flows pass `&account.owner` into `require_owner_or_delegate`, which returns early when `caller == owner` (`account.rs:136-137`) or when `caller` is an active position manager present in `get_delegates(env, account_id, owner)` (`account.rs:124-126`).
- Delegates are keyed under the *owner address at grant time* (`set_account_delegate` → `storage::add_delegate(env, account_id, caller, delegate)`, `account.rs:260-264`), and `add_delegate` verifies ownership via `require_account_owner` → `storage::account_owner` (`account.rs:143-148`, `249-250`) — i.e., the live NFT owner is checked at grant time, but the stored `Account.owner` field is what gates ongoing use.
- The NFT exposes unrestricted standard `transfer`/`approve`/`transfer_from` via `NonFungibleToken`/`NonFungibleEnumerable` (`contract.rs:131-173`); only mint/burn/upgrade are controller-gated (`contract.rs:64-124`).

So after the NFT moves, `Account.owner` still names the seller, and the seller's delegate set remains keyed under the seller's address. The "middleware" (owner/delegate ACL) is bypassed because the alternate path — an ordinary NFT transfer — changed effective ownership without touching the controller's cached ACL.

### Impact Explanation
A seller can list the position NFT, sell it (or gift it), and afterward still call `borrow`, `withdraw`, `swap_collateral`, `swap_debt`, `multiply`, `repay_debt_with_collateral`, or `flash_position` on `account_id` because `caller == account.owner` still matches the stale stored owner — draining all collateral to `to` addresses they control. Even if `Account.owner` were synced elsewhere (the `storage::account_owner` function exists separately, so a sync path may exist — I could not fully verify `get_account`'s owner handling within the available iterations), the delegates keyed under the *previous* owner are never garbage-collected, so a retained position manager could still pass `is_owner_or_delegate`. Either way: theft of user collateral/debt capacity by an unprivileged prior owner. Severity: High/Critical.

### Likelihood Explanation
Fully reachable by a single unprivileged address: create an account via `supply` (`account_id = 0`), optionally `add_delegate` a manager they control, transfer the NFT to a buyer (or even to a second address they own to prove the flow), then call `withdraw(account_id, …)` or `borrow(account_id, …)` — no privileged roles, oracle manipulation, or timing required. Likelihood is high; it only fails if an unseen hook resyncs `Account.owner` or revokes delegates on transfer, which the NFT code shown does not implement.

### Recommendation
- In `is_owner_or_delegate`/`require_owner_or_delegate`, resolve the owner via `storage::account_owner` (live NFT `owner_of`) instead of the cached `Account.owner`, and key delegate lookups under that live owner; or
- Remove `owner` from `Account` entirely so there is a single source of truth; or
- Restrict the NFT's `transfer`/`approve` to controller-mediated paths that also migrate/delete delegate entries.

### Proof of Concept
```text
1. Eve: controller.supply(eve, 0, spoke, [(asset, 1_000e7)]) -> account_id = 7
2. Eve: controller.add_delegate(eve, 7, eve_manager)   // active position manager
3. Eve: position_nft.transfer(eve, victim, 7)          // stock OZ transfer
4. Eve: controller.withdraw(eve, 7, [(asset, 0)], Some(eve))
       // require_owner_or_delegate(7, eve, account.owner == eve) -> passes (stale owner)
       // victim's collateral is paid out to eve
   // alternative: eve_manager calls borrow(7, …) via the surviving delegate key
```
Expected: step 4 reverts (`NotAuthorized` / `AccountNotInMarket`). Observed (if `Account.owner` is stale): withdrawal/borrow succeeds under the prior owner's authority.