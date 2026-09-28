### Title
Stale `account.owner` lets a former NFT owner retain spending authority after transferring the position NFT - (File: contracts/controller/src/account.rs)

### Summary
The Rancher advisory describes a user who deletes a resource but keeps permissions that reference it, then leverages those stale permissions to escalate privileges. The analog here is the controller's two different notions of "owner": spending authority (`borrow`, `withdraw`, strategies, liquidation `Credit` receiver) is checked against the `owner` field stored inside the `Account` struct at creation time, while ownership authority (`add_delegate`, `remove_delegate`, `renew_account`) is checked against the live NFT owner via `storage::account_owner`. Because `position-nft` is a stock OpenZeppelin enumerable NFT whose `transfer`/`transfer_from` do not notify the controller, `account.owner` is not restamped on transfer. A seller therefore retains owner-equivalent spending power over collateral they no longer own.

### Finding Description
`require_owner_or_delegate` in `contracts/controller/src/account.rs` accepts `caller == owner` where `owner` is the `account.owner` field written once by `create_account_with` (`account.rs:64-66`). This field is never updated afterward: the controller exposes no hook invoked on NFT transfer, and `transfer`/`transfer_from` on the NFT contract are stock OZ methods that only move token ownership (see `scripts/permissionless_entrypoints.txt:111`). By contrast, `require_account_owner` (`account.rs:143-148`) reads the *live* owner via `storage::account_owner`, so delegate administration correctly tracks the NFT, but spending authority does not.

Every funds-moving path funnels through the stale check: `process_borrow` calls `require_owner_or_delegate(env, account_id, caller, &account.owner)` at `positions/debt.rs:43`, `process_withdraw` at `positions/supply.rs:150`, and the strategy guards at `account.rs:105-109`. `is_owner_or_delegate` also evaluates the delegate list under the stale `owner` key (`account.rs:124-127`), so delegates granted by the seller remain active too — matching the documented behavior that "a transfer back can reactivate them," which confirms grants are keyed by the old owner address rather than invalidated on transfer.

### Impact Explanation
An attacker supplies collateral, transfers the account NFT to a buyer (e.g., selling a leveraged position), then calls `withdraw`/`borrow` with `caller` = their own address. The stale `account.owner` still equals the attacker, so `require_owner_or_delegate` passes and the attacker drains the buyer's collateral — theft of user funds by a single unprivileged address.

### Likelihood Explanation
Requires only a willing NFT transfer (private sale or OTC deal), which the protocol explicitly supports. No oracle, timing, or privileged action is needed. Caveat: I could not fully verify whether any controller path restamps `account.owner` on transfer — if `storage::account_owner` is also consulted during spending paths or a sync mechanism exists, the finding is mitigated; none was found in `account.rs`, `supply.rs`, or `debt.rs`.

### Recommendation
In `require_owner_or_delegate`/`is_owner_or_delegate`, resolve the owner via `storage::account_owner` (live NFT owner) instead of the cached `account.owner`, or delete `account.owner` entirely and always read the NFT. Alternatively, add an owner-sync step at the top of every spending entrypoint. Also delete the delegate list keyed to the old owner on any detected ownership change, rather than allowing reactivation on transfer-back.

### Proof of Concept
1. Alice calls `supply(Alice, 0, spoke, [(USDC, 1000)])` → account `A`, `account.owner = Alice`.
2. Alice calls `nft.transfer(Alice, Bob, A)` (or `transfer_from` via approval).
3. Alice calls `withdraw(Alice, A, [(USDC, 0)], Some(Alice))`. `require_owner_or_delegate` compares `caller == account.owner` → `Alice == Alice` → passes; solvency check sees no debt → pool pays Bob's collateral to Alice.