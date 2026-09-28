### Title
`flash_position` permanently locks callback-pushed tokens that are neither declared in `collaterals` nor listed in `refund_assets` — ([File: contracts/controller/src/strategies/flash_position.rs])

### Summary
The Allo bug class is "user sends more funds than the declared `amount` parameter and the excess is lost." XOXNO Lending has the same shape on its measured-settlement flash path: `flash_position` credits only balance deltas of assets declared in `collaterals`, refunds only deltas of assets listed in `refund_assets`, and any other token the callback pushes to the controller — or any excess of the debt token that is not refund-listed — is stranded in the controller with no credit and no recovery path.

### Finding Description
`Controller::flash_position(caller, account_id, spoke_id, mode, debt, amount, receiver, data, collaterals, refund_assets)` mints `amount` of debt, forwards the measured receipt to the receiver, and invokes the receiver's `execute_flash_position` callback, which pushes tokens to the controller via plain `token::transfer`. After the callback returns, the controller settles by balance deltas:

- `collateral_before` snapshots only the assets in `collaterals` (flash_position.rs:125-129), and `collect_collateral_deposits` deposits only those measured deltas onto the account (line 145-146).
- `refund_before` snapshots only `refund_assets` (line 130), and `refund_listed_assets` returns only those positive deltas to `caller` (line 148). [1](#0-0) 

There is no third settlement leg and no controller sweep/recovery entrypoint. The reference docs confirm the gap: "Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint" and "Returned debt becomes collateral if declared, returns to the caller if refund-listed, or remains uncredited if in neither list." [2](#0-1) [3](#0-2) 

Concretely, the mismatch cases are:

1. The callback pushes a collateral token but the caller forgot that token in `collaterals` (or listed it under a different hub asset, or exceeded `max_supply_positions` so it had to be dropped): the whole pushed amount is stranded.
2. The callback returns unspent debt tokens to the controller but the caller omitted the debt asset from `refund_assets`: the tokens are stranded while the minted debt stays on the account.
3. A malformed `min_amount` plan where the callback over-delivers a token that is neither declared nor refund-listed: the excess over zero credit is stranded.

In all cases the tokens moved but the declared parameters did not cover them — the same `msg.value > amount` mismatch, expressed in push-measurement form.

### Impact Explanation
Permanent freezing/loss of user funds. Tokens pushed to the controller outside the declared `collaterals`/`refund_assets` sets are neither credited as supply nor returned; the controller has no `sweep`, `rescue`, or `skim` entrypoint, and its owned functions only move tokens through `pool_*` calls that require the controller's own invocation context. The stranded tokens also distort the baseline snapshots of future `flash_position` calls (which is why they are not double-counted later — they simply stay locked).

### Likelihood Explanation
Reachable by a single unprivileged caller: `flash_position` requires only `caller.require_auth` and a deployed Wasm receiver, which the caller controls. The loss path is a realistic integration mistake — the protocol's own test suite exercises it (`FlashPositionMode::Undeclared` pushes `extra_asset` to the controller, and the integration flow seeds "donated" controller balances that must stay untouched). Integration docs treat refund-listing the debt token as a required step precisely because omitting it strands the return leg. As with the Allo original, it requires user misconfiguration rather than a protocol edge case, matching Medium severity. [4](#0-3) [5](#0-4) 

### Recommendation
Refund rather than strand undeclared receipts. Options:

- After `process_deposit` and `refund_listed_assets`, iterate the union of `extra_assets` plus the debt asset and return any remaining positive delta to `caller`; for arbitrary undeclared tokens this cannot enumerate all assets, so additionally expose a `sweep(asset, to)` owner/keeper entrypoint, or
- Track receiver-pushed deltas generically by snapshotting all assets the callback could plausibly touch is infeasible on Soroban, so the pragmatic fix is: (a) auto-include the debt asset in the refund set, and (b) add a permissionless `claim_stranded(asset)` that returns a positive controller balance delta attributable to a completed `flash_position` (or simply sends to governance accumulator — the key is that funds are not permanently frozen).

### Proof of Concept
```rust
// Receiver callback pushes collateral (declared) AND an extra token
// (undeclared, not in refund_assets) to the controller.
fn execute_flash_position(env, initiator, account_id, asset, _amount, _fee,
                          amount_received, controller, _data) {
    token::Client::new(&env, &COLL).transfer(&env.current_contract_address(),
        &controller, &collateral_out);
    // user mistake: returns leftover/extra USDC to controller too
    token::Client::new(&env, &USDC).transfer(&env.current_contract_address(),
        &controller, &extra_usdc);
}
// Caller invokes flash_position with collaterals=[(COLL_hub, min)] and
// refund_assets=[] (omits USDC). Call succeeds: COLL delta is deposited,
// extra_usdc delta is measured by neither snapshot set, is not credited,
// and remains on the controller forever — no sweep entrypoint exists.
```
The harness test `test_flash_position_refunds_undeclared_push` demonstrates the exact path: with `refund_assets` populated the extra ETH is returned (`eth_after - eth_before == extra_amount`, supply credit zero); with `refund_assets` empty the same push would stay on the controller uncredited.

### Citations

**File:** contracts/controller/src/strategies/flash_position.rs (L120-148)
```rust
    let (amount_received, collateral_before, refund_before) =
        storage::with_flash_guard(env, || {
            let amount_received =
                mint_and_forward(env, &mut account, debt, amount, receiver, &mut cache);
            // Baselines exclude funding and forwarding; count callback receipts only.
            let collateral_before = snapshot_balances(
                env,
                &controller,
                collaterals.iter().map(|(hub_asset, _)| hub_asset.asset),
            );
            let refund_before = snapshot_balances(env, &controller, refund_assets.iter());
            invoke_receiver(
                env,
                receiver,
                caller,
                account_id,
                &debt.asset,
                amount,
                amount_received,
                &controller,
                data,
            );
            (amount_received, collateral_before, refund_before)
        });

    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);
```

**File:** docs/reference/endpoints.md (L84-86)
```markdown
Refund assets must be unique, listed in the debt hub and account spoke, disjoint from collateral declarations, and bounded by the maximum supply-position count. Refund eligibility requires an active spoke and an existing listing; it does not check collateralizable, borrowable, paused or frozen flags. Only positive balance changes above pre-callback balances return to the caller. The debt token can be a refund asset, but refunding it does not repay the minted debt.

Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint. Refunds produce token transfer events, without a dedicated controller refund event.
```

**File:** docs/reference/invariants.md (L686-689)
```markdown
scaled debt and the account must retain supply. Returned debt becomes
collateral if declared, returns to the caller if refund-listed, or remains
uncredited if in neither list. Refunds cover only positive callback balance
changes.
```

**File:** tests/test-harness/src/receivers/flash_position.rs (L161-178)
```rust
            FlashPositionMode::Undeclared => {
                if request.collateral_amount > 0 {
                    push_token(
                        &env,
                        &request.collateral,
                        request.collateral_amount,
                        &controller,
                    );
                }
                if request.extra_amount > 0 {
                    push_token(
                        &env,
                        &request.extra_asset,
                        request.extra_amount,
                        &controller,
                    );
                }
            }
```

**File:** tests/test-harness/tests/strategy/flash_position.rs (L237-267)
```rust
fn test_flash_position_refunds_undeclared_push() {
    let mut t = setup();
    let receiver = t.deploy_flash_position_receiver();
    let extra = t.resolve_asset("ETH");
    let extra_amount = f64_to_i128(0.5, t.resolve_market("ETH").decimals);
    let req = FlashPositionRequest {
        mode: FlashPositionMode::Undeclared,
        collateral: t.resolve_asset("USDC"),
        collateral_amount: usdc_raw(&t, 4_000.0),
        extra_asset: extra.clone(),
        extra_amount,
        reenter_spoke_id: HARNESS_SPOKE,
        reenter_account_id: 0,
    };
    let mut refunds = Vec::new(&t.env);
    refunds.push_back(extra.clone());
    let caller = t.get_or_create_user(ALICE);
    let eth_before = soroban_sdk::token::Client::new(&t.env, &extra).balance(&caller);

    let account_id = t
        .try_alice_eth_flash(
            &receiver,
            &data(&t, req),
            &collaterals(&t, &[("USDC", 4_000.0)]),
            &refunds,
        )
        .expect("undeclared refund");
    assert!(account_id > 0);
    let eth_after = soroban_sdk::token::Client::new(&t.env, &extra).balance(&caller);
    assert_eq!(eth_after - eth_before, extra_amount);
    assert_eq!(t.supply_balance_for(ALICE, account_id, "ETH"), 0.0);
```
