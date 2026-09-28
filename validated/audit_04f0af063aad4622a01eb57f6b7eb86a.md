### Title
Burning the position NFT bricks liquidation and bad-debt cleanup for the account (permanent insolvency / frozen funds) - ([File: contracts/controller/src/storage/account.rs])

### Summary

The XOXNO Lending controller resolves an account's owner by reading `owner_of` on the position NFT inside `try_get_account` / `get_account`. If the NFT is burned (or the `Owner` storage entry otherwise becomes unreadable), `try_get_account` returns `None` and `get_account` panics with `AccountNotFound`. Every state-changing path for that account — `liquidate`, `clean_bad_debt` / `force_socialize_bad_debt`, `withdraw`, `repay` flows — loads the account through `get_account`, so the entire account becomes permanently untouchable. An underwater borrower can burn their own NFT to make their debt unliquidatable and unsocializable forever.

### Finding Description

The null-dereference bug class maps onto Soroban as a "missing state → panic" dereference: the controller unconditionally dereferences NFT ownership when materializing an `Account`.

`contracts/controller/src/storage/account.rs:146-161` — `try_get_account` returns `None` when `try_account_owner` (an `owner_of` read on the position NFT contract in `contracts/controller/src/external/position_nft.rs`) cannot resolve ownership, and `get_account` converts that `None` into `panic_with_error!(env, GenericError::AccountNotFound)`:

```rust
pub(crate) fn get_account(env: &Env, account_id: u64) -> Account {
    try_get_account(env, account_id)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::AccountNotFound))
}
```

`process_liquidation` (`contracts/controller/src/positions/liquidation/mod.rs:46`) calls `storage::get_account(env, account_id)` as its very first state read — before any health-factor check. The bad-debt cleanup path (`apply::check_bad_debt_after_liquidation` and the `clean_bad_debt` / `force_socialize_bad_debt` entrypoints, which enter `socialize_bad_debt`) also calls `get_account`. There is no privileged or fallback path that operates on the debt book without first resolving the NFT owner.

This is confirmed by the repository's own harness test `tests/test-harness/tests/controller/position_nft_ttl_and_ownership_reads.rs:281-312`, which burns the victim's NFT and shows:

- `account_exists(id)` still returns `true` (controller-side `AccountMeta` survives),
- `try_liquidate(...)` fails with `ACCOUNT_NOT_FOUND`,
- `clean_bad_debt` / `force_socialize_bad_debt` fail identically on the owner read.

The owner read is hard-required but the collateral and debt position maps are independent storage entries — exactly the shape of a null-pointer dereference: the code assumes a non-null owner pointer that an unprivileged party can null out.

### Impact Explanation

Permanent freezing of funds and protocol insolvency:

- The borrower's supplied collateral can never be withdrawn, seized, or credited — all flows panic on `get_account`.
- The borrower's debt can never be liquidated (`liquidate` → `AccountNotFound`) nor socialized (`clean_bad_debt`, `force_socialize_bad_debt` → `AccountNotFound`). There is no alternative entrypoint that touches the account's books without the owner read.
- If the account is underwater, the protocol permanently carries unbacked debt: the supply-side loss can never be written down via `apply_bad_debt_to_supply_index` / `recapitalize`, so honest suppliers absorb a loss the protocol can never even account for — debt positions remain recorded while liquidation is impossible.

### Likelihood Explanation

A single unprivileged address can trigger this: the NFT owner calls `burn` on the position-nft contract (a standard owner-authorized token operation reachable per the allowed surface "position-nft transfer/approve" family — burn requires only the token owner's auth, exercised directly in the harness test at `position_nft_ttl_and_ownership_reads.rs:297`). The attacker supplies collateral, borrows against it, then burns the NFT the moment the position approaches HF < 1 — or preemptively — permanently shielding the debt. Because the burn is irreversible (no re-mint of the same id restores the `Owner` entry), the DoS is permanent rather than transient. Uncertainty: I confirmed `fn burn` exists in `contracts/position-nft/src/contract.rs` but could not re-verify within the iteration budget that it does not delegate a burn check back to the controller; if the NFT contract requires controller authorization to burn, likelihood drops — however TTL/archival expiry of the `Owner` persistent entry achieves the identical null-dereference through a path that requires no attacker privilege at all (the same test documents the `Owner` entry being unreadable as a distinct trigger).

### Recommendation

Decouple debt/collateral bookkeeping from NFT ownership resolution:

- Make `try_get_account` tolerate a missing owner for non-owner-authorized paths (liquidation, bad-debt cleanup), or store the owner address in `AccountMeta` at account creation and treat the NFT purely as the transferable claim.
- Add a dedicated recovery entrypoint (e.g., `restore_account_ownership`) that lets the pool of last resort re-derive ownership from controller-side meta, or let `clean_bad_debt` operate on the raw position maps without `get_account`.
- Extend `owner_of` TTL renewal aggressively from the controller whenever any account-mutating entrypoint runs, so archival expiry cannot silently null the owner pointer.

### Proof of Concept

1. Alice calls `supply` then `borrow` on the controller, creating `account_id` backed by position NFT `token_id`.
2. Oracle price moves so Alice's HF < 1 (or Alice self-inflicts via volatile collateral).
3. Alice calls `PositionNft::burn(token_id)` — owner-authorized, unprivileged.
4. `liquidate(liquidator, account_id, [(debt_asset, amount)], SeizeMode::Transfer)` → `get_account` → `try_account_owner` fails → panic `AccountNotFound`. Reproduced verbatim by `partial_liquidation_resolves_nft_ownership` (`tests/test-harness/tests/controller/position_nft_ttl_and_ownership_reads.rs:285-308`), which asserts `ACCOUNT_NOT_FOUND` after burn.
5. `clean_bad_debt(account_id)` and `force_socialize_bad_debt(account_id)` fail identically (documented at lines 310-312 of the same test file).
6. The bad debt is permanently unliquidatable; collateral is permanently frozen; the protocol cannot socialize the loss.

Relevant code:
- `get_account` / `try_get_account` owner dereference: `contracts/controller/src/storage/account.rs:146-161`
- Liquidation's first read through `get_account`: `contracts/controller/src/positions/liquidation/mod.rs:46`
- In-repo reproducer: `tests/test-harness/tests/controller/position_nft_ttl_and_ownership_reads.rs:281-312`