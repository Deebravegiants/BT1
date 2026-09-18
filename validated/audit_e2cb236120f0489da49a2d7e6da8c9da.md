### Title
Deposit instruction lacks a mandatory minimum-LP-output check, exposing depositors to unlimited slippage from front-running - (File: `program/src/processor.rs`)

### Summary
`Processor::process_deposit` only bounds the *input* token amounts (`max_coin_amount`, `max_pc_amount`, and an *optional* `other_amount_min`) but never checks a minimum amount of LP tokens the depositor is willing to accept. Because `mint_lp_amount` is derived from the live, un-pinned vault balances at execution time, an attacker who alters those balances immediately before the victim's deposit transaction lands can shrink the LP amount the victim receives while still passing all of the existing (optional) checks — mirroring exactly the "minting lacks slippage protection" bug class from the referenced report.

### Finding Description
The `DepositInstruction` struct only carries bounds on the two input token legs, not on the LP output: [1](#0-0) 

In `process_deposit`, the deposit ratio and the amount of LP to mint are computed from the *current* vault balances (`total_coin_without_take_pnl` / `total_pc_without_take_pnl`), fetched fresh at execution time: [2](#0-1) 

For the `base_side == 0` (base-coin) path, the coin amount deposited is fixed at `deposit.max_coin_amount`, the pc amount is derived from the pool ratio and only checked against the *ceiling* `max_pc_amount` and an *optional* `other_amount_min`: [3](#0-2) 

Critically, `other_amount_min` is `Option<u64>` — callers are not required to supply it, and the CLI even defaults it to unset (`another_min_limit: false`): [4](#0-3) 

Even when `other_amount_min` is supplied, it only bounds the *other input token* amount (`deduct_pc_amount` / `deduct_coin_amount`), not the actual `mint_lp_amount` the user receives: [5](#0-4) 

Because `amm_coin_vault_info` / `amm_pc_vault_info` are ordinary SPL token accounts, anyone can transfer tokens into them directly (no swap needed) between when the victim signs a deposit transaction and when it lands. Inflating one side of the vault balance shifts `InvariantPool`'s `token_total` denominator used in `exchange_token_to_pool`, silently reducing `mint_lp_amount` for the same fixed `deduct_coin_amount`, while still satisfying `deduct_pc_amount <= max_pc_amount` (and even `other_amount_min`, if it is set loosely or not set at all). The victim's deposited coin/pc is fully consumed, but they receive fewer LP tokens than the exchange rate they observed when building the transaction.

### Impact Explanation
A depositor can receive materially fewer LP tokens than expected for the tokens they deposit, i.e., a direct value transfer from the depositor to whoever manipulates the vault balance beforehand (e.g., an MEV searcher/front-runner or the pool's other LPs). This is a concrete value-loss vector for an unprivileged liquidity provider using the standard `Deposit` instruction, consistent with a High-severity slippage-protection gap.

### Likelihood Explanation
The attack requires only sending a permissionless token transfer to the AMM's public coin/pc vault ATAs immediately before a victim's deposit transaction is included — something any actor with mempool visibility (or simply racing transactions) can do without any special privilege. Given `other_amount_min` is optional and defaults to unset in the reference CLI/client, most callers who don't explicitly opt in have zero protection on the actual LP output.

### Recommendation
Add a mandatory `min_lp_amount` (or similar) parameter to `DepositInstruction`, and check `mint_lp_amount >= min_lp_amount` before minting, mirroring the existing `ExceededSlippage` pattern already used for swaps and withdraws (`swap.max_amount_in < swap_in_after_add_fee` and `withdraw.min_coin_amount`/`min_pc_amount`): [6](#0-5) [7](#0-6) 
This closes the gap for both `base_side` branches by directly bounding what the depositor actually cares about — the LP tokens minted — rather than only bounding the input token legs.

### Proof of Concept
1. Victim builds a `Deposit` transaction with `base_side = 0`, `max_coin_amount = X`, `max_pc_amount = Y` (computed from the pool's current ratio), and no `other_amount_min` (the CLI default).
2. Before the victim's transaction is processed, an attacker sends an SPL token transfer of additional coin tokens directly into `amm_coin_vault_info` (a normal token account, no special authority needed to receive tokens).
3. When the victim's transaction executes, `total_coin_without_take_pnl` is now larger; `deduct_coin_amount` is still `X` (fixed), so `mint_lp_amount = InvariantPool{token_input: X, token_total: total_coin_without_take_pnl}.exchange_token_to_pool(amm.lp_amount, Floor)` yields a smaller LP amount than the victim expected.
4. `deduct_pc_amount` (computed from the now-skewed ratio) may still fall at or below `max_pc_amount`, so the `ExceededSlippage` check at `program/src/processor.rs:1206-1222` does not trigger, and since `other_amount_min` is `None`, the check at `program/src/processor.rs:1224-1242` is skipped entirely.
5. The deposit succeeds, transferring the victim's full `X`/`deduct_pc_amount` tokens into the vaults per `program/src/processor.rs:1327-1340`, but mints fewer LP tokens than the victim's expected exchange rate, resulting in a silent value loss.

### Citations

**File:** program/src/instruction.rs (L56-65)
```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct DepositInstruction {
    /// Pool token amount to transfer. token_a and token_b amount are set by
    /// the current exchange rate and size of the pool
    pub max_coin_amount: u64,
    pub max_pc_amount: u64,
    pub base_side: u64,
    pub other_amount_min: Option<u64>,
}
```

**File:** program/src/processor.rs (L1147-1177)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
        let invariant = InvariantToken {
            token_coin: total_coin_without_take_pnl,
            token_pc: total_pc_without_take_pnl,
        };
```

**File:** program/src/processor.rs (L1200-1250)
```rust
        if deposit.base_side == 0 {
            // base coin
            deduct_pc_amount = invariant
                .exchange_coin_to_pc(deposit.max_coin_amount, RoundDirection::Ceiling)
                .ok_or(AmmError::CalculationExRateFailure)?;
            deduct_coin_amount = deposit.max_coin_amount;
            if deduct_pc_amount > deposit.max_pc_amount {
                encode_ray_log(DepositLog {
                    log_type: LogType::Deposit.into_u8(),
                    max_coin: deposit.max_coin_amount,
                    max_pc: deposit.max_pc_amount,
                    base: deposit.base_side,
                    pool_coin: total_coin_without_take_pnl,
                    pool_pc: total_pc_without_take_pnl,
                    pool_lp: amm.lp_amount,
                    calc_pnl_x: target_orders.calc_pnl_x,
                    calc_pnl_y: target_orders.calc_pnl_y,
                    deduct_coin: deduct_coin_amount,
                    deduct_pc: deduct_pc_amount,
                    mint_lp: 0,
                });
                return Err(AmmError::ExceededSlippage.into());
            }
            // base coin, check other_amount_min if need
            if deposit.other_amount_min.is_some() {
                if deduct_pc_amount < deposit.other_amount_min.unwrap() {
                    encode_ray_log(DepositLog {
                        log_type: LogType::Deposit.into_u8(),
                        max_coin: deposit.max_coin_amount,
                        max_pc: deposit.max_pc_amount,
                        base: deposit.base_side,
                        pool_coin: total_coin_without_take_pnl,
                        pool_pc: total_pc_without_take_pnl,
                        pool_lp: amm.lp_amount,
                        calc_pnl_x: target_orders.calc_pnl_x,
                        calc_pnl_y: target_orders.calc_pnl_y,
                        deduct_coin: deduct_coin_amount,
                        deduct_pc: deduct_pc_amount,
                        mint_lp: 0,
                    });
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1779-1786)
```rust
        if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
            if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
                if withdraw.min_coin_amount.unwrap() > coin_amount
                    || withdraw.min_pc_amount.unwrap() > pc_amount
                {
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
```

**File:** program/src/processor.rs (L2205-2207)
```rust
        if swap.max_amount_in < swap_in_after_add_fee {
            return Err(AmmError::ExceededSlippage.into());
        }
```

**File:** README.md (L136-149)
```markdown
3. deposit assets to an amm pool
```rust
// build deposit instruction
let subcmd = AmmCommands::Deposit {
    pool_id: Pubkey::from_str("The specified pool of the assets deposite to").unwrap(),
    deposit_token_coin: Some(Pubkey::from_str("The specified token coin of the user deposit").unwrap()),
    deposit_token_pc: Some(Pubkey::from_str("The specified token pc of the user deposit").unwrap()),
    recipient_token_lp: Some(Pubkey::from_str("The specified lp token of the user will receive").unwrap()),
    amount_specified: 100000u64,
    another_min_limit: false,
    base_coin: false,
};
let instruction = amm_cli::process_amm_commands(subcmd, &config).unwrap();
```
```
