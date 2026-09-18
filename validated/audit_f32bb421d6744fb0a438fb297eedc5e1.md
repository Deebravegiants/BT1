### Title
LP mint amount on Deposit is derived from raw SPL vault balances, not a tracked invariant, allowing donation-based share dilution analogous to Hundred Finance's exchange-rate manipulation - ([File: program/src/processor.rs])

### Summary
Hundred Finance was drained because its `exchangeRateStored`/redemption math derived the hToken↔underlying rate directly from the token contract's raw balance (`balanceOf`), which an attacker could inflate with a plain donation transfer, then exploit a rounding error to redeem a huge amount of underlying for a negligible number of shares. Raydium's `Deposit` instruction has the analogous root-cause pattern: the LP-mint ratio is computed from the AMM vault's live SPL token balance rather than an internally-accounted invariant, and that balance can be inflated by any unprivileged actor sending tokens directly to the vault.

### Finding Description
In `process_deposit`, the pool's total reserves are read straight from the vaults via `Self::unpack_token_account` and `Calculator::calc_total_without_take_pnl_no_orderbook`, using `amm_coin_vault.amount` / `amm_pc_vault.amount` [1](#0-0) . These totals are then used as the denominator for LP-mint calculations:

```
let invariant_coin = InvariantPool { token_input: deduct_coin_amount, token_total: total_coin_without_take_pnl };
mint_lp_amount = invariant_coin.exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)...
``` [2](#0-1) 

`total_coin_without_take_pnl`/`total_pc_without_take_pnl` come directly from the vault's SPL token account balance, not from an amount that only changes through `Deposit`/`Withdraw`/`Swap` instructions. The vaults are ordinary SPL token accounts owned by the AMM authority PDA [3](#0-2) , and standard SPL `transfer`/`transferChecked` only requires the *sender* to sign — the receiving account owner has no say. Any unprivileged actor can therefore submit a plain token transfer directly into `amm_coin_vault` (or `amm_pc_vault`) to inflate its balance without going through `Deposit`, exactly like the WBTC "donation" to the empty hWBTC contract in the Hundred Finance exploit.

Because `mint_lp_amount` is computed as `deduct_coin_amount * amm.lp_amount / total_coin_without_take_pnl` (floor-rounded) [4](#0-3) , an attacker who is the majority/sole existing LP holder can:
1. Donate a large amount of one side's token directly to the vault, inflating `total_coin_without_take_pnl` (or `total_pc_without_take_pnl`) without minting any LP tokens for themselves.
2. Wait for (or induce) a victim `Deposit`; the victim's `mint_lp_amount` is computed against the inflated denominator and rounds down dramatically (potentially toward zero), while their contributed tokens still land in the vault.
3. Withdraw their (still near-100%) LP share, which now entitles them to the pooled reserves including the victim's newly added, under-compensated deposit — the same "inflate the denominator, then capture the redemption" pattern as Hundred's exchange-rate donation attack, just applied to Raydium's `InvariantPool.exchange_token_to_pool` instead of Compound's `exchangeRateStored`.

The pool init logic (`process_initialize2`) does subtract a virtual minimum-liquidity offset from the minted amount (`liquidity - 10^decimals`) while keeping `amm.lp_amount` at the un-discounted `liquidity` value [5](#0-4) , which raises the bar for a brand-new empty pool, but it does not protect an *existing* pool's later depositors from a determined LP holder donating funds directly to the vault before a deposit lands, since `total_coin_without_take_pnl`/`total_pc_without_take_pnl` are re-read from the live vault balance on every `Deposit`/`Withdraw` call.

### Impact Explanation
If exploitable, this allows an attacker who holds (or acquires) a dominant LP share in a given pool to dilute a victim's deposit and later withdraw a disproportionate amount of pool assets, i.e., theft of LP funds / insolvent LP accounting for the victim — matching the "Medium/High, concrete theft or unbacked LP minting" bar in scope.

### Likelihood Explanation
The likelihood depends on attacker economics that I could **not fully verify from static code reading alone**: the attack requires (a) the attacker to control a large majority of a pool's existing `lp_amount` (which they can arrange cheaply for low-TVL/newly-created pools, since anyone can call `Initialize2`), and (b) a victim `Deposit` to land after the donation while the vault balance is still inflated. I was unable to confirm from the indexed code whether any additional safeguard (e.g., a minimum LP output check, or reconciliation between tracked and live balances) exists elsewhere in the deposit path that would block this, since `DepositInstruction` (in `program/src/instruction.rs`) does not appear to expose a `min_lp_amount` slippage parameter — only `other_amount_min`, which bounds the *other token amount*, not the LP tokens minted. This makes the dilution effect on `mint_lp_amount` itself unprotected by user-supplied slippage in the code I reviewed.

### Recommendation
- Track pool reserves internally (increment/decrement only via `Deposit`/`Withdraw`/`Swap` accounting) instead of trusting the live SPL vault balance for LP-mint/redeem ratio calculations, or reconcile/cap the vault balance used in the ratio to the last-known accounted balance plus expected swap fees.
- Add a `min_lp_amount` (or equivalent) slippage-protection parameter to `Deposit` so depositors can bound the LP tokens they are willing to receive, preventing silent dilution from a manipulated denominator.
- Consider validating that vault balance changes between transactions match expected swap/deposit/withdraw deltas, rejecting deposits when unexplained ("donated") balance increases are detected.

### Proof of Concept
Conceptual PoC (could not be executed/tested in this environment):
1. Attacker calls `Initialize2` (or acquires majority LP in an existing low-liquidity pool), becoming the dominant holder of `amm.lp_amount`.
2. Attacker sends a plain SPL `Transfer`/`TransferChecked` instruction (not through the Raydium program) moving a large amount of the coin token directly into `amm_coin_vault`, inflating `amm_coin_vault.amount` without affecting `amm.lp_amount`.
3. A victim submits `Deposit` with `base_side = 0` (base coin) and some `max_coin_amount`/`max_pc_amount`. `mint_lp_amount` is computed via `InvariantPool.exchange_token_to_pool` against the now-inflated `total_coin_without_take_pnl` [6](#0-5) , yielding far fewer LP tokens than the fair-value contribution warrants.
4. Attacker calls `Withdraw` with their LP tokens, redeeming a share of the pool (via `exchange_pool_to_token`) [7](#0-6)  that now includes the victim's under-compensated deposit.

I could not confirm end-to-end exploit profitability (fees, minimum-liquidity offset economics, and whether any un-indexed validation blocks step 2/3) without running the actual program logic in a test harness, so this should be validated with an on-chain/localnet simulation before treating it as fully confirmed.

### Citations

**File:** program/src/processor.rs (L850-880)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_coin_vault.owner,
            *amm_authority_info.key,
            "coin_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_coin_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
        check_assert_eq!(
            *amm_coin_mint_info.key,
            amm_coin_vault.mint,
            "coin_mint",
            AmmError::InvalidCoinMint
        );
        // unpack and check token_pc
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_pc_vault.owner,
            *amm_authority_info.key,
            "pc_vault_owner",
            AmmError::InvalidOwner
        );
```

**File:** program/src/processor.rs (L908-917)
```rust
        let liquidity = Calculator::to_u64(
            U128::from(amm_pc_vault.amount)
                .checked_mul(amm_coin_vault.amount.into())
                .unwrap()
                .integer_sqrt()
                .as_u128(),
        )?;
        let user_lp_amount = liquidity
            .checked_sub((10u64).checked_pow(lp_mint.decimals.into()).unwrap())
            .ok_or(AmmError::InitLpAmountTooLess)?;
```

**File:** program/src/processor.rs (L1138-1153)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        let user_source_coin =
            Self::unpack_token_account(&user_source_coin_info, spl_token_program_id)?;
        let user_source_pc =
            Self::unpack_token_account(&user_source_pc_info, spl_token_program_id)?;
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1243-1250)
```rust
            // coin_amount/ (total_coin_amount + coin_amount)  = output / (lp_mint.supply + output) =>  output = coin_amount / total_coin_amount * lp_mint.supply
            let invariant_coin = InvariantPool {
                token_input: deduct_coin_amount,
                token_total: total_coin_without_take_pnl,
            };
            mint_lp_amount = invariant_coin
                .exchange_token_to_pool(amm.lp_amount, RoundDirection::Floor)
                .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1751-1761)
```rust
        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/math.rs (L456-477)
```rust
    /// Exchange rate
    pub fn exchange_token_to_pool(
        &self,
        pool_total_amount: u64,
        round_direction: RoundDirection,
    ) -> Option<u64> {
        Some(if round_direction == RoundDirection::Floor {
            U128::from(pool_total_amount)
                .checked_mul(self.token_input.into())
                .unwrap()
                .checked_div(self.token_total.into())
                .unwrap()
                .as_u64()
        } else {
            U128::from(pool_total_amount)
                .checked_mul(self.token_input.into())
                .unwrap()
                .checked_ceil_div(self.token_total.into())
                .unwrap()
                .as_u64()
        })
    }
```
