### Title
Unenforced cross-parameter invariant between `min_gas_purchase_price` and `account_creation_charge` can silently undercharge account creation - (File: runtime/runtime/src/lib.rs)

### Summary
The CCTP bug is a class of "two independently hard-coded/configured values are assumed compatible (max fee vs. minimum required fee) but nothing in the code enforces that relationship, so the assumption can silently break." The nearest reachable analog in nearcore is the relationship between the protocol parameters `min_gas_purchase_price` and `account_creation_charge`. `Runtime::refund_unspent_gas_and_deposits` assumes `min_gas_purchase_price * create_account_gas_cost >= account_creation_charge` and only checks this via `debug_assert!`, which is compiled out in production (release) builds. If a future protocol-version config update ever changes these two parameters independently (as has already happened once at PV 85, `85.yaml`) without preserving this inequality, account creation would be silently undercharged rather than erroring, exactly like CCTP's hard-coded fee failing to track an externally-set minimum.

### Finding Description
`account_creation_charge` is levied on new accounts by capping the amount charged to `burned_gas_refund`, which is itself bounded by the gas purchased at `min_gas_purchase_price`: [1](#0-0) 

Specifically:
- `desired_cost = config.account_creation_charge`
- `amount_to_charge = desired_cost.saturating_sub(burned_cost)`
- `amount_actually_charged = min(amount_to_charge, burned_gas_refund)`

The code then documents and "checks" the required invariant only with `debug_assert!`:
```
// sanity check: purchasing gas at `min_gas_purchase_price` should be enough to cover
// the cost of creating an account.
debug_assert!(
    safe_gas_to_balance(config.min_gas_purchase_price, create_account_gas_cost)
        .unwrap()
        >= desired_cost
);
``` [2](#0-1) 

`debug_assert!` is a no-op in release builds, which is what production validator nodes run. `min_gas_purchase_price` and `account_creation_charge` are two entirely independent, hard-coded runtime-config parameters, both introduced/changed together only by hand in the same protocol-version diff file: [3](#0-2) 

There is no code path (config loading, `RuntimeConfig` construction, or config-store validation) that computes and enforces `min_gas_purchase_price * action_create_account.execution.gas >= account_creation_charge`; the relationship is maintained purely by developer discipline when authoring new protocol-version YAML diffs. This is structurally identical to the CCTP root cause: a value meant to act as a floor/ceiling for another quantity (max fee vs. minimum fee; here, gas-purchase price vs. account-creation charge) is hard-coded/configured independently, with no dynamic or enforced coupling, so a future change to one side alone silently breaks the assumption relied upon elsewhere in the code.

### Impact Explanation
If a future protocol upgrade raises `account_creation_charge` (e.g., to track NEAR price or increase state-bloat deterrence) without proportionally raising `min_gas_purchase_price` (or vice versa lowers `min_gas_purchase_price`), the invariant breaks in production silently (no panic, since `debug_assert!` is stripped in release). The consequence is that `amount_actually_charged` is capped at `burned_gas_refund`, which can be less than the intended `desired_cost`, so `AccountCostIncrease`'s account-creation charge is under-collected. This is a concrete instance of "free or underpriced execution" — the protocol fails to charge the accounting fee it is supposed to charge for account creation, silently, without any error surfaced to operators or users, and without failing any test unless a debug build is used.

This differs from the CCTP report's fail-closed behavior (reverts) — nearcore's version fails open (silently undercharges) — which arguably makes it a more severe variant of the same bug class, since underpricing produces no error signal at all, only a slow economic loss to the protocol.

### Likelihood Explanation
This requires a future protocol-version config change; at the current mainnet parameter values (PV 86) the margin is very large (`min_gas_purchase_price` × `create_account` exec gas ≫ `account_creation_charge`), so the issue is latent rather than currently triggerable. Likelihood of exploitation today is low, but the underlying code weakness — an economically important invariant checked only by a debug-only assertion, with no compile-time or config-load-time enforcement — is a real defect that would activate automatically the next time these two parameters are tuned independently, which the codebase has already done once (PV 85 changed both together, by hand).

### Recommendation
Replace the `debug_assert!` with either:
1. A hard runtime check (`assert!`/explicit error) that fires in release builds and prevents applying a config that violates the invariant, or
2. A validation step in `RuntimeConfig`/`config_store.rs` construction that rejects any protocol-version config where `min_gas_purchase_price * create_account_exec_gas < account_creation_charge`, causing a startup-time failure rather than a silent runtime undercharge, or
3. Derive `account_creation_charge` from `min_gas_purchase_price` and the `create_account` fee at charge time (bound `desired_cost` by `min(desired_cost, min_gas_purchase_price * create_account_gas_cost)`) so the charge can never exceed what the purchased gas guarantees, removing the assumption entirely.

### Proof of Concept
This is a configuration-triggered defect, not one exploitable via a single transaction today:
1. Author a future protocol-version YAML diff (e.g., `core/parameters/res/runtime_configs/NN.yaml`) that raises `account_creation_charge` (e.g., to `1 N`) while leaving `min_gas_purchase_price` unchanged (`1_000_000_000` yN/gas) or lowers `min_gas_purchase_price` while leaving `account_creation_charge` unchanged, such that `min_gas_purchase_price * create_account_exec_gas < account_creation_charge`.
2. Run a release-mode nearcore node (no `debug_assertions`) with this config activated.
3. Submit a `CreateAccount` transaction that succeeds via `AccountCostIncrease`'s gas-purchase/refund path (`refund_unspent_gas_and_deposits`, `runtime/runtime/src/lib.rs:1230`).
4. Observe that `amount_actually_charged` is clamped to `burned_gas_refund` (line 1323: `std::cmp::min(amount_to_charge, burned_gas_refund)`), which is less than the configured `account_creation_charge`, with no error emitted — the account is created for less than the intended protocol charge, and the `debug_assert!` sanity checks at lines 1327–1337 never fire because they are compiled out in release builds. [1](#0-0) [3](#0-2)

### Citations

**File:** runtime/runtime/src/lib.rs (L1306-1344)
```rust
        // If an account was created, charge more to cover its cost.
        if created_account && ProtocolFeature::AccountCostIncrease.enabled(protocol_version) {
            // This is how much creating an account should cost
            let desired_cost = config.account_creation_charge;

            let create_account_gas_cost =
                config.fees.fee(ActionCosts::create_account).exec_fee().gas;
            // The cost of the gas that was burned already
            let burned_cost = safe_gas_to_balance(gas_burn_price, create_account_gas_cost)?;

            // We would like to charge as much as needed to reach desired_cost
            let amount_to_charge = desired_cost.saturating_sub(burned_cost);

            // We can't charge more than `burned_gas_refund`.
            // `burned_gas_refund < amount_to_charge` could happen for receipts where the gas was
            // purchased in protocol versions before `ProtocolFeature::AccountCostIncrease`, at a lower
            // gas price that isn't enough to cover the cost of creating an account.
            let amount_actually_charged = std::cmp::min(amount_to_charge, burned_gas_refund);

            // sanity check: purchasing gas at `min_gas_purchase_price` should be enough to cover
            // the cost of creating an account.
            debug_assert!(
                safe_gas_to_balance(config.min_gas_purchase_price, create_account_gas_cost)
                    .unwrap()
                    >= desired_cost
            );

            // sanity check: as long as the purchase price is high enough, there should always be
            // enough refund balance to cover the cost of creating an account.
            if gas_purchase_price >= config.min_gas_purchase_price {
                debug_assert!(burned_gas_refund >= amount_to_charge);
            }

            // Subtract `amount_actually_charged` from the refund.
            gas_refund_result.create_account_charge = amount_actually_charged;
            burned_gas_refund = burned_gas_refund
                .checked_sub(amount_actually_charged)
                .expect("burned_gas_refund >= amount_actually_charged checked above");
        }
```

**File:** core/parameters/res/runtime_configs/85.yaml (L40-43)
```yaml
# Minimum price at which gas attached to a receipt is purchased.
min_gas_purchase_price: { old: 0, new: 1_000_000_000 }
# How much creating a new account should cost.
account_creation_charge: { old: 0, new: 0.007 N }
```
