### Title
Unprivileged dust top-up force-restamps a foreign account's LTV and gated liquidation tuple without the owner's consent - (File: contracts/controller/src/positions/supply.rs)

### Summary
The controller intentionally lets any authenticated third party top up an *existing* supply asset of a foreign account (`require_third_party_existing_supply`, INV-AUTH-03). Every supply leg, including a 1-strotop dust top-up, runs `merge_supply_leg` → `refresh_supply_risk_params`, which unconditionally rewrites the victim position's stored `loan_to_value` and, through `apply_gated_liquidation_params`, restamps `liquidation_threshold`, `liquidation_bonus`, and `liquidation_fees` to the live listing values whenever the liquidator-favoring change leaves hypothetical HF ≥ 1.05. This is the same bug class as `userLastDepositTime[user] = block.timestamp` on a dust deposit: a dust transfer by an arbitrary caller stamps new, worse state onto a user who never consented.

### Finding Description
Supply positions snapshot their risk terms at creation (`get_or_create_supply_position`) and are supposed to keep them until a refresh path runs (docs/reference/runbooks/liqvid-listing-params.md §10). Three refresh paths exist: owner supply, non-liquidation withdrawal, and `update_account_threshold`. Critically, the supply path is reachable by **any** caller, because `process_supply` only requires that the topped-up `hub_asset` already exists in `account.supply_positions` when `account_id != 0` and the caller is not owner/delegate: [1](#0-0) 

Inside `merge_supply_leg`, `refresh_supply_risk_params` first overwrites `position.loan_to_value = effective_config.loan_to_value` with no gate at all, then `apply_gated_liquidation_params` applies a liquidator-favoring tuple (lower LT, higher bonus, or lower fee) whenever the account's HF computed with the new LT is ≥ `THRESHOLD_UPDATE_MIN_HF_RAW` (1.05) — or unconditionally for debt-free accounts: [2](#0-1) [3](#0-2) 

After a listing edit that favors liquidators (e.g., LT 8000 → 6100, bonus +500 bps, fee −50 bps — exactly the shape exercised in `test_update_account_threshold_propagates_adverse_tuple_to_healthy_account`), an attacker can pick the moment HF ≥ 1.05 and force the worse tuple onto a victim with a dust top-up, rather than letting the victim keep the old stamped terms until they voluntarily act. The victim has no way to block or revert the restamp.

### Impact Explanation
- Lower `liquidation_threshold` directly lowers HF, making the account liquidatable at higher collateral prices than under its stamped terms — the victim can be liquidated "early," paying the liquidation bonus and fees (theft of user funds via forced liquidation economics).
- Higher `liquidation_bonus` increases the collateral seized per liquidation leg, and lower `liquidation_fees` changes the split — both worsen the victim's loss given liquidation.
- Even when the HF gate blocks the tuple, the unconditional `loan_to_value` restamp silently cuts the victim's borrow limit (min(stored LTV, stored LT) per the runbook), a state degradation imposed by an outsider.
- The dust cost is negligible (one minimal `transfer_amount_measured` leg), mirroring the 1-wei griefing deposit in the source report.

### Likelihood Explanation
Requires a prior governance listing edit that favors liquidators (lower LT / higher bonus / lower fee) — a routine risk-management operation — plus a target account holding that asset with HF ≥ 1.05 under the new LT. Both conditions are common during parameter tightening cycles. The attacker is any authenticated address; no delegation, allowlist, or minimum amount applies, and the target must already hold the asset (the only gate INV-AUTH-03 provides). Note that `update_account_threshold` is also permissionless, so the restamp is reachable regardless — but the supply path additionally lets the attacker restamp *while contributing dust that also changes the victim's position*, and its HF gate is evaluated before the new supply is credited, a nuance documented in the runbook. The permissionless refresh appears to be an intended keeper mechanism, which is why this is Medium rather than High: the harm is forcing adverse terms onto a specific victim at a chosen moment, without consent or recourse.

### Recommendation
- Restrict `refresh_supply_risk_params` in `merge_supply_leg` to owner/delegate-initiated supplies, or pass a flag distinguishing third-party top-ups and skip the param restamp for them (top-up credits shares only).
- Alternatively, apply the `favors_liquidator` gate to *all* third-party refreshes including LTV, and consider requiring HF ≥ 1.05 computed *after* crediting the new collateral so the dust cannot be used to time the restamp.
- Document (or enforce) that permissionless `update_account_threshold` is the only intended foreign-account restamp path, so `supply` cannot be used as a cheaper, consent-free alternative.

### Proof of Concept
1. Alice owns account `A` with a USDC supply position stamped LTV 7500 / LT 8000, and an ETH borrow keeping HF ≈ 1.20.
2. Governance executes `edit_asset_in_spoke` setting USDC to LTV 5000 / LT 6100 / bonus +500 / fee −50 (liquidator-favoring). Alice's stored tuple stays 7500/8000.
3. Attacker Bob calls `supply(caller=Bob, account_id=A, spoke_id, assets=[(hub, USDC, 1)])`. `require_third_party_existing_supply` passes because `A.supply_positions` already contains USDC; `transfer_amount_measured` pulls 1 unit; `merge_supply_leg` calls `refresh_supply_risk_params`.
4. `position.loan_to_value` becomes 5000 unconditionally; since hypothetical HF with LT 6100 is still ≥ 1.05, `apply_gated_liquidation_params` also stamps LT 6100, the higher bonus, and the lower fee.
5. Alice's account is now liquidatable at materially higher collateral prices and pays a larger bonus on liquidation — all triggered by Bob's 1-unit deposit, without Alice's consent. This mirrors the test `poc_lt_cut_stays_sticky_when_hf_below_min`, which confirms `try_supply_to_account(BOB, ALICE, "USDC", 1.0)` succeeds and restamps LTV even below the HF gate. [4](#0-3) [5](#0-4) 

Uncertainty noted: I verified `merge_supply_leg` invokes `refresh_supply_risk_params` via the runbook's authoritative mapping (line 384) rather than by reading the function body directly; the runbook states the supply path uses the same `apply_gated_liquidation_params` gate as the other refresh paths (i.e., `FullTuple` scope).

### Citations

**File:** contracts/controller/src/positions/supply.rs (L86-96)
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
```

**File:** contracts/controller/src/risk/params.rs (L34-39)
```rust
    let before = *position;
    position.loan_to_value = effective_config.loan_to_value;
    if scope == RiskRefreshScope::FullTuple {
        apply_gated_liquidation_params(env, cache, account, hub_asset, position, effective_config);
    }
    *position != before
```

**File:** contracts/controller/src/risk/params.rs (L76-93)
```rust
    if favors_liquidator(position, effective_config)
        && !account.debt_free()
        && !clears_min_hf(
            env,
            cache,
            account,
            hub_asset,
            position,
            effective_config.liquidation_threshold,
        )
    {
        return;
    }

    position.liquidation_threshold = effective_config.liquidation_threshold;
    position.liquidation_bonus = effective_config.liquidation_bonus;
    position.liquidation_fees = effective_config.liquidation_fees;
}
```

**File:** tests/test-harness/tests/controller/security_audit.rs (L489-499)
```rust
    t.try_supply_to_account(BOB, ALICE, "USDC", 1.0)
        .expect("top-up must remain allowed");
    let (ltv_after, lt_after) = supply_ltv_and_lt(&t, id, "USDC");
    assert_eq!(
        ltv_after, 5_000,
        "H-RISK-03/04: LTV always restamps on supply refresh"
    );
    assert_eq!(
        lt_after, 8_000,
        "H-RISK-04: LT stamp must stay sticky when post-cut HF < 1.05"
    );
```

**File:** docs/reference/runbooks/liqvid-listing-params.md (L384-399)
```markdown
| A supply of the asset into the account | `merge_supply_leg` calls `refresh_supply_risk_params` |
| A withdrawal of the asset that is not a liquidation and leaves a balance | `merge_withdraw_leg` |
| `update_account_threshold(caller, has_risks = true, account_ids)` | `sync_account_thresholds` |

A liquidation never refreshes them. `update_account_threshold` with
`has_risks = false` refreshes the LTV only.

All three paths use the same gate (`apply_gated_liquidation_params`). A
change favours the liquidator when it lowers LT, raises the bonus or lowers
the fee. For an account with debt, such a change applies only when the
account HF, calculated with the new LT, is at least 1.05
(`THRESHOLD_UPDATE_MIN_HF_RAW`). If the HF is lower, the position keeps its
old LT, bonus and fee, and the call does not fail. A debt-free account always
takes the new values. In the supply path, the gate calculates the HF before
the new supply adds to the collateral. The gate reads the prices of all
assets of the account. When the gate runs, a stale price or a price outside
```
