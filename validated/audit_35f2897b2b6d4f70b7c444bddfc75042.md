### Title
Stale `Account.owner` recorded at mint is used for owner/delegate authorization, so a transferred position NFT leaves the prior owner acting as the account's principal - (File: contracts/controller/src/account.rs)

### Summary
`is_owner_or_delegate` / `require_owner_or_delegate` authorize `caller` by comparing against `account.owner`, the address stored in the `Account` struct when the NFT was minted (`create_account` lines 62-70), not against the live NFT owner (`storage::account_owner`, used by `require_account_owner` at line 145). The position NFT has no transfer hook back to the controller, so `Account.owner` is never resynced after `transfer`/`transfer_from` on the position NFT. A credential (ownership) valid at issuance therefore remains bound to the wrong principal — the direct analog of a certificate chain that validates but isn't bound to the requesting client.

### Finding Description
- `create_account` snapshots `owner` into `Account { owner, ... }` at mint time (contracts/controller/src/account.rs:62-70).
- Delegate grants are keyed under that same stored owner: `storage::get_delegates(env, account_id, owner)` and `add_delegate`/`remove_delegate` write under `caller` (account.rs:124-127, 260-264).
- `require_owner_or_delegate` returns early when `caller == account.owner` (account.rs:121-122, 136-139), guarding `load_or_create_account` for `AccountGuard::Migrate` and `AccountGuard::Multiply` (account.rs:101-109).
- In contrast, `require_account_owner` uses the live NFT owner via `storage::account_owner` (account.rs:143-147), and the docs state the NFT "is the live ownership authority". The two checks disagree exactly when the NFT has been transferred.
- `renew_account`, `add_delegate`, `remove_delegate` call `caller.require_auth()` plus `require_account_owner` — the ex-owner fails these, but `require_owner_or_delegate` never consults the NFT, so `caller.require_auth()` by the stale owner is sufficient for Migrate/Multiply paths (multiply, migrate_from_blend) and any other entrypoint reaching those guards. The result is a stored, never-invalidated credential.

### Impact Explanation
A seller of a position NFT retains a usable "owner" identity on the controller: they can drive `multiply` and `migrate_from_blend` on an account they no longer own, reshaping its debt/collateral and routing its swap legs through self-controlled venues (routes are unallowlisted per the threat model) to siphon value, or grief the position below liquidation threshold and capture the bonus as a liquidator. Conversely the true NFT owner fails `require_owner_or_delegate`, so delegate-granting, migration, and multiply flows break for them — a permanent functional impairment of the purchased position until it is emptied and recreated. Both theft-of-value and freezing-of-use effects arise from one unprivileged `transfer` followed by an unprivileged controller call.

### Likelihood Explanation
Anyone who ever held the NFT retains the stale authority; selling positions on secondary markets, or acquiring an NFT via liquidation-adjacent transfer and then transacting before the original owner notices, are natural triggers. The attack needs only the ex-owner's signature — no privileged role, no oracle manipulation, no timing race. The only uncertainty I could not fully resolve is whether another write path resyncs `Account.owner` on NFT transfer; the NFT contract exposes no controller notification (transfers are plain `require_auth` on the token owner), and no code path I found writes `account.owner` after mint, so the stale binding appears to persist for the account's lifetime.

### Recommendation
In `require_owner_or_delegate` (and delegate storage keys), resolve the live owner via `storage::account_owner(env, account_id)` / `nft.owner_of` instead of `Account.owner`, or drop `Account.owner` entirely and treat the NFT as the sole authority. Add a regression test: mint, `transfer` NFT, assert the ex-owner fails `multiply`/`migrate_from_blend` and the new owner succeeds.

### Proof of Concept
1. Alice calls `supply(caller=alice, account_id=0, spoke, market, amount)` → mints NFT `token_id = id`, stores `Account.owner = alice`.
2. Alice transfers NFT `id` to Bob (legitimate sale).
3. Alice (ex-owner) calls `multiply(caller=alice, account_id=id, ...)` — `caller.require_auth()` passes with her own signature, `require_owner_or_delegate` returns early on `caller == account.owner`, so the call proceeds on Bob's account.
4. Bob (live NFT owner) calls `add_delegate`/`multiply` — `require_owner_or_delegate` sees `caller != account.owner` and no delegate entry under `account.owner = alice`, panicking `NotAuthorized`.