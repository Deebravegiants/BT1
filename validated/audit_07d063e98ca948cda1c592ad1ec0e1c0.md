### Title
Stale `account.owner` grants a previous NFT holder continuing borrow/withdraw authority after the account NFT is transferred — ([File: contracts/controller/src/account.rs](contracts/controller/src/account.rs))

### Summary
The kernel bug is a use-after-free: `blk_mq_complete_request` frees a request while `blk_mq_tag_to_rq` still dereferences the stale pointer. The XOXNO Lending analog is a *stale authority* use-after-free: the `Account` struct persists `owner` at creation, and every fund-moving entrypoint authorizes against that stored field via `require_owner_or_delegate`, while actual account ownership lives in the transferable `position-nft` contract. After `position-nft::transfer`, the stored `owner` is a "freed" authority that `borrow`, `withdraw`, `multiply`, `swap_collateral`, `repay_debt_with_collateral`, `flash_position`, `swap_debt`, and `migrate_from_blend` still dereference.

### Finding Description
`load_or_create_account` loads the account and, for the `Multiply`/`Migrate` guards, calls `require_owner_or_delegate(env, account_id, caller, &account.owner)`. `is_owner_or_delegate` returns `true` whenever `caller == account.owner`, and `account.owner` is the address that created the account — a stored field, not the live NFT owner:

- `AccountGuard::Multiply` and `AccountGuard::Migrate` use `&account.owner` from `storage::get_account` (contracts/controller/src/account.rs:98-111).
- `is_owner_or_delegate` grants authority when `caller == owner` (account.rs:120-127).
- `require_account_owner` — used only by `renew_account`, `add_delegate`, `remove_delegate` — is the *only* check that resolves live NFT ownership via `try_account_owner`/`nft_try_owner_of_call` (account.rs:143, storage/account.rs:35-44).

The NFT contract is a stock OpenZeppelin enumerable NFT; `transfer`/`transfer_from` move the token with no controller hook, so nothing rewrites `account.owner` (scripts/permissionless_entrypoints.txt:111-113; docs/reference/endpoints.md:49 — "NFT ownership ... transfers atomically"). The documentation only states that a transfer *deactivates the previous owner's delegate grants*; it says nothing about the previous owner itself losing authority — and it cannot, because the comparison is against the stale stored field.

Concrete path: victim buys/receives position NFT `token_id = account_id` with supplied collateral. The seller calls `controller::withdraw(caller=seller, account_id, ...)` or `borrow`. `caller.require_auth()` passes (seller signs), `require_owner_or_delegate` passes because `seller == account.owner` (stale), and collateral/debt is drawn against an account the seller no longer owns. Likewise `flash_position`/`multiply` on an existing Multiply-mode account can mint fee-free debt and restructure collateral under the stale owner.

### Impact Explanation
Theft of user funds. Any account whose NFT changes hands (sale, OTC deal, `transfer_from` via approval, wallet migration) remains fully controllable by the prior `account.owner`: collateral can be withdrawn and new debt minted against the new owner's position. This directly breaks the documented invariant that "NFT ownership, including control of collateral and the debt obligation, transfers atomically" (endpoints.md:49).

### Likelihood Explanation
High whenever accounts change hands. The vulnerable entrypoints are unprivileged (`caller-auth` in the declared exception list) and require only that the caller was the *original* creator — no delegate grant, no NFT ownership at call time. Account trading/transfer is an explicitly supported feature (position-nft is a standard enumerable NFT), so the condition is reached by any `position-nft::transfer` of a funded account.

### Recommendation
Authorize against live NFT ownership, not the stored field. Either:
- Replace `&account.owner` in `is_owner_or_delegate`/`require_owner_or_delegate` with `storage::account_owner(env, account_id)` (the live `nft_try_owner_of_call` result), and key delegate lookups to that live owner; or
- Keep `account.owner` as a cache but re-stamp it from the NFT owner at the top of every entrypoint before the guard runs.

Delegate storage keys must then be indexed by the live owner consistently so a transferred account's old grants cannot be reactivated by the seller.

### Proof of Concept
```text
1. ALICE calls controller::supply(account_id=0, USDC, 10_000) → account 7 created;
   Account.owner = ALICE persisted; NFT #7 minted to ALICE.
2. ALICE calls position-nft::transfer(ALICE → BOB, 7).
   The NFT contract has no controller hook; Account.owner remains ALICE.
3. ALICE calls controller::withdraw(caller=ALICE, account_id=7, USDC leg).
   - caller.require_auth() → ALICE signs.
   - load_or_create_account → storage::get_account(7).owner == ALICE.
   - require_owner_or_delegate → caller == account.owner → passes
     (account.rs:121 `caller == owner` on the stale field).
   - Collateral leaves to ALICE; BOB holds NFT #7 over a drained account.
Same primitive: borrow/mint debt, swap_collateral to a worthless asset,
or flash_position on a Multiply-mode account — all authorized by the stale owner.
```

Uncertainty note: I verified the two-tier check (`require_owner_or_delegate` on stored `account.owner` vs `require_account_owner` on live NFT) and that no NFT-transfer hook exists, but I could not fully enumerate every write site of `Account.owner`; if some finalize path silently re-stamps `owner` from the NFT on each entrypoint, the bug collapses — that code was not observed in the inspected files (`account.rs`, `storage/account.rs`, `positions/`), and the existence of a separate `require_account_owner` live-NFT check strongly indicates the stored field is *not* refreshed.