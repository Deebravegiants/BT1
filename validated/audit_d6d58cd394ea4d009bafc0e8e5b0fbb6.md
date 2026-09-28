### Title
Front-running account creation lets an attacker claim a predicted `account_id` and capture a victim's deposit - (File: contracts/controller/src/positions/supply.rs)

### Summary
The original finding is a front-running/setup-injection class: a predictable, permissionless creation path lets an attacker seize a resource the victim expects to own, and a missing validation lets the victim's own transaction fund the attacker's object. XOXNO Lending has the same shape. Position-NFT token ids (which equal `account_id`) are minted from a monotonic sequential counter, so the next id is publicly predictable. `supply` with `account_id = 0` creates an account owned by the caller, while `supply` into an existing account does not require the caller to be the owner or a delegate — it only requires the supplied hub assets to already exist on the account (`require_third_party_existing_supply`, INV-AUTH-03). An attacker can therefore front-run a victim's `supply(caller, account_id = N)` that targets a not-yet-minted id, claim `N` for itself, seed the victim's declared assets with dust, and let the victim's transaction deposit real funds into the attacker's account.

### Finding Description
`process_supply` resolves the target through `load_or_create_account` with `AccountGuard::Supply`. For an existing id, the `Supply` guard only calls `require_spoke_match` — it never checks `require_owner_or_delegate`: [1](#0-0) 

Ownership of a new account is bound to `caller` only in the `account_id == 0` branch, and for non-owners the sole restriction is that each supplied `hub_asset` must already be a supply position on the account: [2](#0-1) 

Because the position NFT issues ids from `increment_token_id`, a monotonic counter that `burn` never decrements or reuses, the id that a victim's "create and fund" flow will mint is externally observable: [3](#0-2) 

The attack mirrors the reported one:

1. The victim builds a funding transaction `supply(caller = victim, account_id = N, spoke_id = S, assets = [USDC amount])` where `N` is the id they expect to own (e.g., precomputed from `total_supply`, or replayed after an earlier create attempt failed post-simulation).
2. The attacker front-runs with `supply(caller = attacker, account_id = 0, spoke_id = S, assets = [dust of the victim's exact hub assets])`. The sequential counter assigns the attacker `N`; the NFT mints to the attacker.
3. The victim's transaction now executes against an existing, attacker-owned account. `require_third_party_existing_supply` passes because the attacker seeded exactly the markets the victim lists; `process_deposit` pulls the victim's tokens into the pool and credits measured receipts to account `N` via `merge_supply_leg`. [4](#0-3) 

4. The attacker, as NFT owner of `N`, calls `withdraw` to extract the victim's collateral. The victim's transaction returns `N` and `account_exists(N)` is true, so the victim may believe they own the account — the same deception as in the original report — while `owner_of(N)` is the attacker.

### Impact Explanation
Theft of user funds. The victim's entire deposited amount is credited as collateral to an account the attacker owns and can immediately withdraw, subject only to spoke exit flags. Without the front-run the victim's transaction would revert (`AccountNotFound` on a nonexistent id), so the attacker converts a failed transaction into a successful transfer of value to itself — precisely the "user's transaction fails, but the attacker profits" inversion of the HOPR finding.

### Likelihood Explanation
The attack needs the victim to submit `supply` with a nonzero `account_id` they do not own. This is realistic for integrators and scripts that precompute the next token id from the enumerable extension (`total_supply` / `get_token_id`) instead of passing `0`, or that retry a previously simulated create-and-fund transaction after the first attempt reverted. The controller explicitly documents that third-party top-ups are permissionless, so nothing in the victim's transaction signals a problem. The attacker only needs to observe the pending transaction (Soroban mempool / RPC submission channel), front-run with dust, and match the spoke and asset list — all visible in the victim's submitted arguments. Cost is a dust deposit and one transaction fee; the payout is the victim's full deposit.

### Recommendation
Bind supply credit to ownership intent. Two mitigations, either sufficient:

- When `account_id != 0`, require `require_owner_or_delegate` unless the caller explicitly opts into a donation path (e.g., a separate `donate` entrypoint or a `beneficiary` flag that clearly credits a foreign account).
- Keep the permissionless top-up but reject the call when `account.owner != caller` and the caller did not authorize the deposit as a top-up — at minimum, document loudly that supplying to an id the caller does not own is a donation, and have SDK helpers refuse a nonzero `account_id` whose `owner_of` differs from the caller.

Optionally, emit an event or return code distinguishing "credited a foreign account" from "credited own account" so clients and wallets can surface the squatted-id case.

### Proof of Concept
```rust
// Attacker observes victim's pending tx:
//   supply(caller = victim, account_id = N, spoke_id = S,
//          assets = [(usdc_key, 1_000e7)])
// where N == next sequential token id (unminted).

// Step 1: front-run — claim id N and seed the victim's declared markets.
ctrl.supply(&attacker, &0, &S, &vec![&env, (usdc_key, dust)]);
assert_eq!(nft.owner_of(&N), attacker);

// Step 2: victim's tx lands. Supply guard passes: spoke matches and the
// account already holds a USDC supply position (attacker's dust).
ctrl.supply(&victim, &N, &S, &vec![&env, (usdc_key, 1_000e7)]);

// Step 3: attacker owns N and withdraws the victim's collateral.
ctrl.withdraw(&attacker, &N, &vec![&env, (usdc_key, 0)], &None);
// attacker holds ~1_000e7 USDC of the victim's funds; victim holds nothing.
```
Relevant guards: `AccountGuard::Supply` performs no owner check (`contracts/controller/src/account.rs:99-111`), the non-owner path only enforces pre-existing supply positions (`contracts/controller/src/positions/supply.rs:78-97`), and id predictability comes from the monotonic NFT counter (`contracts/position-nft/README.md:152-154`).

### Citations

**File:** contracts/controller/src/account.rs (L99-111)
```rust
    match guard {
        AccountGuard::Supply => require_spoke_match(env, &account, spoke_id),
        AccountGuard::Migrate => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
        }
        AccountGuard::Multiply => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
            assert_with_error!(env, account.mode == mode, GenericError::AccountModeMismatch);
        }
    }
    (account_id, account)
```

**File:** contracts/controller/src/positions/supply.rs (L86-97)
```rust
    if account_id != 0
        && !account::is_owner_or_delegate(env, resolved_account_id, caller, &account.owner)
    {
        for (hub_asset, _) in aggregated.iter() {
            assert_with_error!(
                env,
                account.supply_positions.contains_key(hub_asset.clone()),
                GenericError::NotAuthorized
            );
        }
    }
}
```

**File:** contracts/controller/src/positions/supply.rs (L116-135)
```rust
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
    }

    let results = pool_supply_call(env, &pool_addr, &entries);
    for_each_leg(env, &entries, &results, |entry, result| {
        merge_supply_leg(env, account, &entry.action, &result, cache);
    });
```

**File:** contracts/position-nft/README.md (L150-154)
```markdown
their own token either: no holder-facing burn entrypoint exists.

**Token ids are never reused.** Ids come from `increment_token_id`, a
monotonic instance counter. `burn` does not decrement it. A burned id can never
be minted again, so a deleted account id cannot be resurrected.
```
