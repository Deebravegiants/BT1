### Title
Reserve-compression LP mint/burn manipulation via disproportionate deposit-to-swap ratio - (File: `program/src/processor.rs`)

### Summary
Raydium's `Deposit` instruction mints LP tokens using a simple ratio of the single-sided deposit amount to the *current* pool reserve (`total_coin_without_take_pnl` / `total_pc_without_take_pnl`), with no floor on how small that reserve can be. If a swapper first drives one side of the pool reserve down to a very small integer value via a large `SwapBaseIn`/`SwapBaseOut` trade, a subsequent `Deposit` denominated in the depleted side can mint a grossly disproportionate amount of LP tokens for a negligible deposit, mirroring the Balancer V1 rounding/compression exploit pattern (compress reserve near-zero, then mint LP disproportionately).

### Finding Description
`process_deposit` computes `mint_lp_amount` from `InvariantPool::exchange_token_to_pool`, which is `pool_total_amount (amm.lp_amount) * token_input (deduct_coin_amount or deduct_pc_amount) / token_total (total_coin_without_take_pnl or total_pc_without_take_pnl)`, floored: [1](#0-0) [2](#0-1) 

The only zero-guard present is `amm.lp_amount == 0` (`NotAllowZeroLP`) at pool-empty state; there is no check that `total_coin_without_take_pnl` or `total_pc_without_take_pnl` (the *denominator* used for the ratio) remains above a meaningful minimum: [3](#0-2) 

Both reserves are attacker-observable/attacker-influenceable in the same transaction context because `SwapBaseIn`/`SwapBaseOut` use the standard constant-product formula with no minimum-reserve floor beyond integer division rounding: [4](#0-3) 

If an attacker (via flash loan or large capital) swaps a very large amount of `pc` into the pool (or `coin`), the opposing reserve (`coin`, or `pc`) can be driven down to a very small residual integer amount (e.g. single digits), while `amm.lp_amount` (LP supply) remains unchanged by the swap. The attacker then calls `Deposit` with `base_side` selecting the depleted token as the "base" side with a minimal amount (e.g. `deduct_coin_amount = 1`). Because `mint_lp_amount = amm.lp_amount * deduct_coin_amount / total_coin_without_take_pnl`, when `total_coin_without_take_pnl` is compressed to a tiny value (e.g. `1`), `mint_lp_amount` approaches `amm.lp_amount` itself — i.e., the attacker can mint LP tokens comparable to the entire existing supply while depositing a negligible `deduct_coin_amount` (and a correspondingly small/derived `deduct_pc_amount` via `exchange_coin_to_pc`, which is priced off the same manipulated reserve ratio and therefore also small).

This closely tracks the reported Balancer V1 root cause: an attacker uses a large trade to compress one reserve towards its rounding floor, then exploits the ratio-based LP-mint formula (which assumes reserves are proportionally representative of pool value) to mint LP tokens far in excess of the value actually contributed. The attacker can subsequently `Withdraw` those LP tokens (burn) to claim a share of the *other*, undepleted reserve (and to recover the depleted reserve after later swapping back / letting it refill via later trades), draining real value from existing LPs.

### Impact Explanation
This is a direct threat to pool solvency and existing LP funds: an attacker can mint LP tokens disproportionate to value deposited, then redeem them via `Withdraw`'s proportional payout (`InvariantPool::exchange_pool_to_token`) to claim a share of the pool's *other* token reserve that they did not fairly contribute, diluting/stealing value from legitimate liquidity providers. This matches the "unbacked LP minting / insolvent pool accounting" impact class explicitly in scope.

### Likelihood Explanation
The attack is reachable from a single submitted transaction (or small transaction sequence) by any unprivileged trader/LP using attacker-chosen accounts and data: `SwapBaseIn`/`SwapBaseOut` to compress a reserve, followed by `Deposit` with `base_side` set to the compressed token and a small `max_*_amount`/`other_amount_min`. No privileged signer or special build is required. The severity of the disproportion scales with how much capital the attacker can bring (flash loans on Solana are less standardized than EVM, but a well-capitalized attacker or repeated compounding trades could still achieve significant compression, especially on pools with modest liquidity). The `checked_ceil_div`/`checked_div` in `InvariantPool`/`InvariantToken` will not revert on a small denominator as long as it's nonzero, so no built-in protection stops this beyond ordinary slippage limits (`other_amount_min`, `max_pc_amount`) which the attacker controls and can set to permissive values matching their own attack input.

### Recommendation
Introduce a minimum-reserve/minimum-liquidity floor analogous to constant-product AMM protections (e.g., require `total_coin_without_take_pnl` and `total_pc_without_take_pnl` to remain above a protocol-defined minimum after any swap, and/or reject `Deposit` when the ratio-denominator reserve used for `exchange_token_to_pool` is below a safe threshold relative to `amm.lp_amount`/decimals). Additionally, consider requiring deposits to be validated against both sides' implied `mint_lp_amount` (already partially done via `deduct_pc_amount`/`deduct_coin_amount` cross-checks) and enforcing a minimum absolute deposit size or a maximum single-swap price-impact cap to prevent reserve compression to near-zero within a single transaction/slot.

### Proof of Concept
1. Attacker observes an AMM pool with reserves `coin = C`, `pc = P`, `lp_amount = L` (`amm.lp_amount`).
2. Attacker submits `SwapBaseIn`/`SwapBaseOut` with a large `amount_in` of `pc`, driving `total_coin_without_take_pnl` down to a minimal residual value `coin' ≈ 1` (per the constant-product formula in `swap_token_amount_base_in`, `program/src/math.rs:300-325`), while `total_pc_without_take_pnl` grows to `pc' ≈ (C*P)/coin'`.
3. In the same or a following transaction, attacker calls `Deposit` with `base_side = 0` (base `coin`) and `max_coin_amount = 1` (i.e., `deduct_coin_amount = 1`), `max_pc_amount` set permissively high enough to satisfy `deduct_pc_amount = invariant.exchange_coin_to_pc(1, Ceiling)` (`program/src/processor.rs:1200-1250`).
4. `mint_lp_amount = InvariantPool{token_input: 1, token_total: coin'}.exchange_token_to_pool(L, Floor)` (`program/src/math.rs:456-477`) evaluates to `L * 1 / coin'`, which for `coin' = 1` yields `mint_lp_amount ≈ L` — i.e., attacker mints LP tokens roughly equal to the *entire* existing LP supply for depositing 1 unit of `coin` (plus a proportional `pc` amount priced off the manipulated ratio).
5. Attacker calls `Withdraw` with the newly minted LP tokens, receiving a proportional share of `total_pc_without_take_pnl`/`total_coin_without_take_pnl` per `InvariantPool::exchange_pool_to_token` (`program/src/processor.rs:1751-1761`), extracting value disproportionate to their actual deposit and diluting/stealing from existing LPs.

Note: I could not fully verify from static code review alone whether Raydium's swap fee structure and available capital constraints (no native Solana flash-loan primitive referenced in this program) make step 2's extreme compression practically achievable within one atomic transaction at scale for a well-funded pool; this would need dynamic/economic simulation (e.g., with realistic pool sizes and swap fee %) to confirm the achievable compression ratio and resulting `mint_lp_amount` magnitude.

### Citations

**File:** program/src/processor.rs (L1180-1196)
```rust
        if amm.lp_amount == 0 {
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
                deduct_coin: 0,
                deduct_pc: 0,
                mint_lp: 0,
            });
            return Err(AmmError::NotAllowZeroLP.into());
        }
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

**File:** program/src/math.rs (L300-325)
```rust
                // => amount_out = pc - coin * pc / (coin + amount_in)
                // => amount_out = ((pc * coin + pc * amount_in) - coin * pc) / (coin + amount_in)
                // => amount_out =  pc * amount_in / (coin + amount_in)
                let denominator = total_coin_without_take_pnl.checked_add(amount_in).unwrap();
                amount_out = total_pc_without_take_pnl
                    .checked_mul(amount_in)
                    .unwrap()
                    .checked_div(denominator)
                    .unwrap();
            }
            SwapDirection::PC2Coin => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (pc + amount_in) * (coin - amount_out) = coin * pc
                // => amount_out = coin - coin * pc / (pc + amount_in)
                // => amount_out = (coin * pc + coin * amount_in - coin * pc) / (pc + amount_in)
                // => amount_out = coin * amount_in / (pc + amount_in)
                let denominator = total_pc_without_take_pnl.checked_add(amount_in).unwrap();
                amount_out = total_coin_without_take_pnl
                    .checked_mul(amount_in)
                    .unwrap()
                    .checked_div(denominator)
                    .unwrap();
            }
        }
        return amount_out;
    }
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
