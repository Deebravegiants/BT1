### Title
Controller accepts token transfers but has no sweep or recovery path — stray and undeclared callback balances are permanently locked - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
The XOXNO Lending `controller` contract can hold token balances — it receives them every time a `flash_position` receiver pushes collateral back, or any time an unprivileged address calls `token.transfer(controller, …)` directly — but it exports no entrypoint that can move an arbitrary balance back out. Unlike `contracts/swap-aggregator`, which ships an owner-only `sweep_balance` for exactly this case (`contracts/swap-aggregator/src/lib.rs:189-202`), the controller has no `sweep`/`recover`/`skim` function at all. The documentation states this plainly: "Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint." (`docs/reference/endpoints.md:86`).

### Finding Description
The `flash_position` strategy is permissionless: `process_flash_position` authenticates only the `caller`, mints debt into the controller, and invokes a caller-chosen Wasm `receiver` callback (`contracts/controller/src/strategies/flash_position.rs:40-111`). After the callback returns, the controller measures balance deltas and only acts on two declared sets:

1. `collaterals` — each declared `HubAssetKey`'s measured delta is checked against its minimum and deposited as supply (`validate_collaterals`, `contracts/controller/src/strategies/flash_position.rs:103`).
2. `refund_assets` — positive deltas for these explicitly listed token addresses are refunded to the caller (`validate_refund_assets`, `contracts/controller/src/strategies/flash_position.rs:104-111`).

Any token the receiver transfers to the controller that is not in either list — a wrong token, an extra token from a swap, a misdeclared refund asset, or simply a plain token transfer sent to the controller address at any time — is neither credited nor refunded. Because the refund set must be disjoint from collateral declarations and bounded, and there is no catch-all "return everything left over" step, the residual tokens sit on the controller forever.

The test suite codifies this behavior: `test_migrate_refund_ignores_preexisting_controller_balance` mints ETH directly to the controller, runs a migration, and asserts the pre-existing balance "must remain (not used as refund or swept)" (`tests/test-harness/tests/strategy/migrate_blend.rs:529-535`). A grep over `contracts/controller`, `contracts/pool`, `contracts/governance`, and `contracts/position-nft` finds no `fn sweep`, `fn recover`, `fn rescue`, or `fn skim` in any of them — only the out-of-scope swap-aggregator exports one.

Root cause: the controller's settlement model is strictly whitelist-of-declared-assets plus measured deltas, with no administrative or permissionless recovery path for whatever falls outside the declarations.

### Impact Explanation
Any token balance that reaches the controller outside a declared collateral/refund slot is permanently frozen — the accepted "permanent freezing of funds" impact class. Concretely:

- A `flash_position` caller whose receiver contract over-transfers an undeclared token (e.g., a multi-output swap leg, or a receiver bug) loses those funds permanently; there is no later call that returns them.
- Anyone can grief-lock tokens onto the controller via a direct `token.transfer`, but more importantly a caller's own stray balance sent during composition is unrecoverable regardless of value.
- The same applies to `migrate_from_blend` refund caps: funds pulled into the controller above the declared `cap` (the `(eth, cap)` entries in `migrate_from_blend`) are left on the controller with no exit (`tests/test-harness/tests/strategy/migrate_blend.rs:529-535` confirms the residual just sits there).

Because Soroban tokens cannot be burned/withdrawn by the holder of a contract address without the contract cooperating, the lock is absolute absent a code upgrade.

### Likelihood Explanation
Medium-likelihood, matching the original report's Medium severity. Reaching it requires an unprivileged-path action — a direct token transfer to the controller, or a `flash_position` receiver that pushes an undeclared asset — both of which are explicitly in the allowed entrypoint set. Misdeclared refund/collateral lists in flash callbacks are a realistic integrator error (the callback pushes tokens via plain `transfer`, and the controller silently drops anything undeclared rather than reverting), and the code chooses not to refund leftover controller balances even when it can measure them, so the failure is silent rather than loud.

### Recommendation
Mirror the swap-aggregator's pattern: add an owner-gated (or governance-operation) `sweep_balance(recipient, tokens)` on the controller that transfers balances not accounted for by any in-flight strategy, or add a generic refund step in `process_flash_position` that returns positive deltas for any non-collateral asset received during the callback instead of restricting refunds to a declared list. At minimum, revert when the controller ends a `flash_position` call with an unexpected positive delta in an undeclared asset, so integrator errors fail loudly instead of locking funds.

### Proof of Concept
```rust
// An unprivileged caller locks tokens on the controller permanently.
// 1. Direct path: any token holder
token::Client::new(&env, &usdc).transfer(&victim, &controller, &1_000);
//    -> controller balance = 1_000; no entrypoint exists to move it out.

// 2. flash_position path: receiver pushes an undeclared asset.
//    Inside FlashPositionReceiver::execute_flash_position the receiver does:
token::Client::new(&env, &stray_token).transfer(
    &env.current_contract_address(),
    &controller,
    &stray_out,
);
//    `stray_token` is not in `collaterals` and not in `refund_assets`,
//    so validate/measure steps ignore it and it is never returned.
//    Existing behavior is asserted by
//    tests/test-harness/tests/strategy/migrate_blend.rs:529-535:
//    "pre-existing controller ETH must remain (not used as refund or swept)".
```

Citations: [1](#0-0) , [2](#0-1) , [3](#0-2) , [4](#0-3)

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L103-117)
```rust
    validate_collaterals(env, &mut cache, &account, collaterals);
    validate_refund_assets(
        env,
        &mut cache,
        account.spoke_id,
        debt.hub_id,
        collaterals,
        refund_assets,
    );

    let mut extra_assets = vec![env, debt.asset.clone()];
    for (hub_asset, _) in collaterals.iter() {
        extra_assets.push_back(hub_asset.asset.clone());
    }
    prefetch_strategy_prices(&mut cache, &account, &extra_assets);
```

**File:** docs/reference/endpoints.md (L75-90)
```markdown
`flash_position` requires a debt market with flash loans enabled and a deployed Wasm receiver other than the controller or pool. Its collateral declarations must meet all of these conditions:

- The list is nonempty and does not exceed the maximum supply-position count.
- Markets and underlying tokens are unique.
- All minimum amounts are nonnegative, with at least one positive minimum.
- Measured controller receipts from the callback meet every minimum.

Pool supply measures receipts again. Borrow and supply caps are checked when each pool result merges into the account. Supply and the declared debt position must remain open after finalization.

Refund assets must be unique, listed in the debt hub and account spoke, disjoint from collateral declarations, and bounded by the maximum supply-position count. Refund eligibility requires an active spoke and an existing listing; it does not check collateralizable, borrowable, paused or frozen flags. Only positive balance changes above pre-callback balances return to the caller. The debt token can be a refund asset, but refunding it does not repay the minted debt.

Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint. Refunds produce token transfer events, without a dedicated controller refund event.

### Revenue and recapitalization

`claim_revenue` forwards the controller's measured receipts to the configured accumulator. A taxed onward transfer can deliver less to the accumulator. Pool revenue measures outstanding claims, not cumulative earnings. Recapitalization applies no more than the market's backing shortfall and refunds excess.
```

**File:** tests/test-harness/tests/strategy/migrate_blend.rs (L496-536)
```rust
#[test]
fn test_migrate_refund_ignores_preexisting_controller_balance() {
    let mut t = LendingTest::new().standard_two_asset().build();
    let caller = t.get_or_create_user(ALICE);
    let blend_addr = register_approved_blend(&t);
    seed_position(&t, &blend_addr, &caller, "USDC", KIND_COLLATERAL, 2000.0);
    seed_position(&t, &blend_addr, &caller, "ETH", KIND_LIABILITY, 0.5);

    let usdc = t.resolve_asset("USDC");
    let eth = t.resolve_asset("ETH");
    let eth_dec = t.resolve_market("ETH").decimals;
    let stuck = f64_to_i128(0.25, eth_dec);
    t.resolve_market("ETH")
        .token_admin
        .mint(&t.controller, &stuck);

    let cap = f64_to_i128(0.6, eth_dec);
    let account_id = t.ctrl_client().migrate_from_blend(
        &caller,
        &0u64,
        &1u32,
        &HARNESS_HUB,
        &blend_addr,
        &SorobanVec::from_array(&t.env, [usdc]),
        &empty_assets(&t),
        &SorobanVec::from_array(&t.env, [(eth.clone(), cap)]),
    );

    let borrow = t.borrow_balance_for(ALICE, account_id, "ETH");
    assert!(
        (0.49..=0.51).contains(&borrow),
        "debt must still reconcile to ~0.5, got {borrow}"
    );
    let controller_eth = t.env.as_contract(&t.controller, || {
        soroban_sdk::token::Client::new(&t.env, &eth).balance(&t.controller)
    });
    assert_eq!(
        controller_eth, stuck,
        "pre-existing controller ETH must remain (not used as refund or swept)"
    );
}
```

**File:** contracts/swap-aggregator/src/lib.rs (L187-203)
```rust
    /// Transfers each token's balance above its reserved fee total to `recipient`. Owner only.
    #[only_owner]
    fn sweep_balance(env: Env, recipient: Address, tokens: Vec<Address>) {
        renew_instance(&env);
        let router = env.current_contract_address();
        let n = tokens.len();
        for i in 0..n {
            // `i < n == tokens.len()`, so the index is in range by construction.
            let token = tokens.get_unchecked(i);
            let client = token::Client::new(&env, &token);
            let balance = client.balance(&router);
            let reserved = storage::reserved_fee_balance(&env, &token);
            if balance > reserved {
                client.transfer(&router, &recipient, &(balance - reserved));
            }
        }
    }
```
