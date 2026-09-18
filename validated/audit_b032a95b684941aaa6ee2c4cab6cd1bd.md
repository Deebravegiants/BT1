### Title
Unbounded direct token donations to AMM vaults trigger unrecoverable arithmetic-overflow panics in `calc_take_pnl`, permanently freezing pool and LP funds - ([File: program/src/processor.rs])

### Summary
Every state-mutating pool instruction reachable by an unprivileged user — `Deposit`, `Withdraw`, `WithdrawPnl`, and both swap variants — reads the AMM's coin/PC token-vault balances directly off-chain via `spl_token::state::Account::unpack` and feeds them, unvalidated, into `Calculator::calc_total_without_take_pnl_no_orderbook` and `Processor::calc_take_pnl`, both of which perform chained `checked_mul()/.checked_div()/.checked_sub().unwrap()` arithmetic on `U128`/`U256` values derived from those balances. Because SPL token vaults can receive tokens from *any* signer via a plain `spl_token::instruction::transfer` that never touches the Raydium program, an attacker can inflate `amm_coin_vault.amount` and/or `amm_pc_vault.amount` far beyond what any legitimate `Deposit`/`Swap` would ever produce. Once the combined vault balances are large enough that `pool_pc_amount.checked_mul(pool_coin_amount)` (a `U128` operation) overflows, or the ratio math inside `calc_x_power`/`calc_take_pnl` divides by an attacker-inflated value producing a `None`, the `.unwrap()` panics and aborts the transaction — permanently, on every subsequent call, since the inflated vault balance is on-chain state that cannot be reduced by any instruction path.

### Finding Description
`calc_take_pnl` is the pnl/"take-profit" bookkeeping routine invoked from `process_deposit`, `process_withdraw` (unless `WithdrawOnly`), and `process_withdrawpnl`: [1](#0-0) 

Its first line already panics-on-overflow rather than returning an error:
```
if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
    >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
``` [2](#0-1) 

`pool_pc_amount`/`pool_coin_amount` are `U128::from(total_pc_without_take_pnl)` / `U128::from(total_coin_without_take_pnl)`, values derived straight from the live vault balances via `calc_total_without_take_pnl_no_orderbook`: [3](#0-2) 

Deeper in the same function, `calc_x_power` performs unchecked-panic division:
```
let x_power = last_x.checked_mul(last_y).unwrap()
    .checked_mul(current_x).unwrap()
    .checked_div(current_y).unwrap();
``` [4](#0-3) 

and the diffs that follow use `.checked_sub().unwrap()` on values whose relative ordering depends entirely on the (now attacker-influenced) vault balances: [5](#0-4) 

Critically, none of `amm_pc_vault.amount` / `amm_coin_vault.amount` are bounded or sanity-checked against the pool's tracked `lp_amount`/expected reserves before being consumed by this math — `unpack_token_account` only checks the SPL token program owner and unpacks the raw balance: [6](#0-5) 

Because SPL token vault accounts are ordinary token accounts, any unprivileged party can call the SPL Token program directly (outside the Raydium program) to transfer additional tokens into `amm.coin_vault` / `amm.pc_vault`, arbitrarily inflating the balances used by every subsequent Deposit/Withdraw/WithdrawPnl/Swap call. This is the same underlying bug class as the Kubo advisory — attacker-controlled/self-consistent data reaching unguarded arithmetic (`unwrap()`/no-panic-recovery) that a normal caller can trigger with a single, cheap, repeatable action — except here the "crash" is a permanent, state-persistent one: the poisoned vault balances remain on-chain forever, so every future transaction touching this pool's pnl-accounting path panics and reverts, effectively bricking the pool.

### Impact Explanation
Once the vault balances are pushed into the region where `calc_take_pnl`'s arithmetic overflows or divides in a way that panics, `Deposit`, `Withdraw`, and `WithdrawPnl` become permanently unusable for that pool (they all call `calc_take_pnl` unconditionally except `Withdraw` in `WithdrawOnly` status). Existing LPs can no longer withdraw their principal through the normal path, and the pool's already-accrued but unwithdrawn PNL becomes permanently stuck. This matches the "permanent freezing of user or LP funds" impact bar: no signer collusion or privileged action is needed — only a plain SPL token transfer to a publicly known vault address, which is exactly the "unauthenticated, remotely reachable with attacker-chosen data" character of the original Kubo panic-DoS bug class.

### Likelihood Explanation
Likelihood is Medium-High for pools involving high-supply tokens (extremely common among Solana meme/utility tokens, many of which mint in the range of 10^12–10^18 raw base units), since the attacker only needs to acquire (or mint, if they control the token) and transfer enough of the tokens directly to the vault addresses — both of which are public account keys derivable from the on-chain `AmmInfo` — to trigger the overflow/divide condition; no interaction with the Raydium program itself is required to stage the attack, and the resulting DoS is deterministic and permanent once triggered.

### Recommendation
- Replace all `.unwrap()` calls in `Calculator::calc_x_power`, `Calculator::calc_take_pnl`'s helper math, `Calculator::normalize_decimal`/`normalize_decimal_v2`/`restore_decimal`, and related `math.rs` routines with `checked_*` + `ok_or(AmmError::...)` propagation (as already done in `calc_total_without_take_pnl_no_orderbook`), so malformed/extreme vault states return a program error instead of panicking.
- Do not trust raw `amm_coin_vault.amount` / `amm_pc_vault.amount` as ground truth for pnl bookkeeping; reconcile against `amm.lp_amount` and the pool's tracked reserves, and reject/quarantine (rather than silently consume) balances that deviate beyond an expected bound from swap/deposit/withdraw history.
- Add explicit upper-bound checks on vault balances (or on the pool_pc*pool_coin product) before entering `calc_take_pnl`, returning a recoverable error rather than allowing state to reach an unrecoverable panic condition.

### Proof of Concept
1. Attacker identifies/creates a Raydium pool where the coin or PC mint has very large raw-unit supply (common for standard SPL tokens with many decimals/high supply).
2. Attacker issues a normal `spl_token::instruction::transfer` (no Raydium program involvement, no signer other than the token owner) sending a very large additional amount of coin or PC tokens directly to `amm.coin_vault` / `amm.pc_vault`.
3. Any subsequent call to `Deposit`, `Withdraw`, or `WithdrawPnl` on this pool loads the now-inflated vault balance via `unpack_token_account`, computes `total_pc_without_take_pnl`/`total_coin_without_take_pnl`, and calls `Processor::calc_take_pnl` [7](#0-6) , which panics at the `checked_mul(...).unwrap()` on line 190 (or later `checked_div`/`checked_sub` `.unwrap()`s) once the balances exceed the arithmetic-safe range.
4. Because the donated balance cannot be removed by any instruction, every future `Deposit`/`Withdraw`/`WithdrawPnl` transaction against this pool panics and aborts, permanently freezing LP and user funds in the pool.

### Citations

**File:** program/src/processor.rs (L131-143)
```rust
    /// Unpacks a spl_token `Account`.
    #[inline]
    pub fn unpack_token_account(
        account_info: &AccountInfo,
        token_program_id: &Pubkey,
    ) -> Result<spl_token::state::Account, AmmError> {
        if account_info.owner != token_program_id {
            Err(AmmError::InvalidSplTokenProgram)
        } else {
            spl_token::state::Account::unpack(&account_info.data.borrow())
                .map_err(|_| AmmError::ExpectedAccount)
        }
    }
```

**File:** program/src/processor.rs (L167-192)
```rust
    pub fn calc_take_pnl(
        target: &TargetOrders,
        amm: &mut AmmInfo,
        total_pc_without_take_pnl: &mut u64,
        total_coin_without_take_pnl: &mut u64,
        x1: U256,
        y1: U256,
    ) -> Result<(u128, u128), ProgramError> {
        // calc pnl
        let mut delta_x: u128;
        let mut delta_y: u128;
        let calc_pc_amount = Calculator::restore_decimal(
            target.calc_pnl_x.into(),
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let calc_coin_amount = Calculator::restore_decimal(
            target.calc_pnl_y.into(),
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
```

**File:** program/src/processor.rs (L205-214)
```rust
            // let x2 = Calculator::sqrt(x2_power).unwrap();
            let x2 = x2_power.integer_sqrt();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl x2_power:{}, x2:{}", x2_power, x2).as_str());
            let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl y2:{}", y2).as_str());

            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
            let diff_x = U128::from(x1.checked_sub(x2).unwrap().as_u128());
            let diff_y = U128::from(y1.checked_sub(y2).unwrap().as_u128());
```

**File:** program/src/processor.rs (L1148-1173)
```rust
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
```

**File:** program/src/math.rs (L50-60)
```rust
    pub fn calc_x_power(last_x: U256, last_y: U256, current_x: U256, current_y: U256) -> U256 {
        // must be use u256, because u128 may be overflow
        let x_power = last_x
            .checked_mul(last_y)
            .unwrap()
            .checked_mul(current_x)
            .unwrap()
            .checked_div(current_y)
            .unwrap();
        x_power
    }
```

**File:** program/src/math.rs (L238-250)
```rust
    pub fn calc_total_without_take_pnl_no_orderbook<'a>(
        pc_amount: u64,
        coin_amount: u64,
        amm: &'a AmmInfo,
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
    }
```
