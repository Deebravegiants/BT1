### Title
Stale `account.owner` retains full spending authority after position NFT transfer - (File: contracts/controller/src/account.rs)

### Summary
The controller maintains two sources of account ownership that can diverge: the `Account.owner` field written once at mint time, and the live position-NFT owner read via `storage::account_owner`. Spending-critical paths (`withdraw`, `borrow`, `multiply`, `swap_*`, `repay_debt_with_collateral`, `migrate_from_blend`) authorize against the stale stored `Account.owner` through `require_owner_or_delegate`, while only delegate/renewal management re-checks the live NFT owner. After a position NFT is transferred, the seller keeps full control of the account's collateral and borrowing power, and the buyer gets nothing — a direct analog of "a low-privilege token can still exercise greater-scope authority."

### Finding Description
`create_account_with` stores `Account { owner: owner.clone(), .. }` at mint (`contracts/controller/src/account.rs:64-70`). Nothing in the controller updates this field on NFT transfer — the NFT contract (`position-nft`) is an external OpenZeppelin enumerable contract with no callback into the controller, so `Account.owner` is frozen at the original minter.

Authorization then splits:

- `require_owner_or_delegate` (`account.rs:130-140`) compares `caller == *owner` where `owner` is the *stored* `Account.owner`, and looks up delegates under `storage::get_delegates(env, account_id, owner)` keyed by that stale owner (`account.rs:126`).
- `require_account_owner` (`account.rs:143-148`) instead reads `storage::account_owner` — the live NFT owner — but it is only used by `add_delegate`, `remove_delegate`, and `renew_account` (`account.rs:221, 250`), never by fund-moving flows.

Concretely, `process_withdraw` calls `require_owner_or_delegate(env, account_id, caller, &account.owner)` (`contracts/controller/src/positions/supply.rs:150`) and pays out to a caller-chosen `recipient` (`supply.rs:152-157`). `resolve_seize_receiver` and every strategy guard use the same stale-field check (`liquidation/mod.rs:180`, `account.rs:101-108`).

Attack path for a single unprivileged address:
1. Create an account via `supply(account_id = 0, ...)`, building collateral and borrow capacity.
2. Transfer the position NFT to a buyer (sale of the account) via `position-nft::transfer`, receiving payment off-chain or atomically.
3. Call `controller::withdraw(account_id, withdrawals, to = attacker)` — `caller == account.owner` still holds for the seller, solvency is checked against the account's own (now buyer-owned) positions, and funds are paid to the attacker.

### Impact Explanation
Theft of user funds. The NFT buyer believes they purchased a lending account (its collateral and debt), but the seller's address remains the spending authority and can withdraw all collateral to an arbitrary recipient (`to` parameter) at any time, or draw new borrows against it via `borrow`/`multiply`. The buyer cannot stop this: `remove_delegate` and `renew_account` authenticate against the NFT owner, but `withdraw`/`borrow` authenticate against the stale stored owner, so the legitimate owner is the one locked out.

### Likelihood Explanation
Any holder of a position NFT can execute this whenever account NFTs change hands — OTC sales, marketplace listings, or even accidental transfers. No protocol precondition (unhealthy HF, specific market state, oracle deviation) is required; the desync exists by construction because `Account.owner` is never resynchronized with NFT ownership. The only mitigation would be a flow that restamps `account.owner` from `storage::account_owner`, and none of the reviewed entrypoints (`supply.rs`, `liquidation/mod.rs`, `account.rs`) performs such a restamp — the permissionless-entrypoints inventory even asserts delegates "go inactive" on transfer, implying the stored owner is treated as immutable. Confidence is moderate-high: the two divergent authority sources are directly visible in the code, though a sync hook elsewhere (not found in the reviewed files) cannot be fully excluded.

### Recommendation
Stop trusting `Account.owner` for spending authority. Either:
- Resolve the owner at call time via `storage::account_owner(env, account_id)` inside `require_owner_or_delegate`, and key delegate storage by `account_id` alone (or by the resolved live owner), or
- Store no `owner` on `Account` at all and always read NFT ownership, removing the possibility of desync.

Also update `is_owner_or_delegate`'s delegate lookup (`account.rs:126`) so grants follow the live owner rather than the historical minter.

### Proof of Concept
1. Attacker calls `controller::supply(0, spoke_id, [payment])` → `create_account` mints NFT to attacker and stores `Account.owner = attacker` (`account.rs:63-70`). Attacker supplies/borrows to build a valuable account.
2. Victim purchases the account; attacker calls `position-nft::transfer(victim, token_id)` — valid under NFT auth (`permissionless_entrypoints.txt:111`).
3. Attacker calls `controller::withdraw(account_id, [(hub_asset, 0 /*withdraw-all*/)], Some(attacker_addr))`:
   - `caller.require_auth()` passes (attacker signs).
   - `require_owner_or_delegate` sees `caller == account.owner` (stale) → passes (`account.rs:121-122`).
   - `settle_withdraw` pays the attacker-specified recipient (`supply.rs:152-215`).
4. Victim's call to `withdraw` reverts: `caller != account.owner`, and delegates keyed under the attacker's owner record do not include the victim → `GenericError::NotAuthorized`.