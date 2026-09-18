## Finding

### Title
Deposit's `other_amount_min` slippage parameter is optional and unenforced when omitted, enabling front-run/sandwich attacks against liquidity depositors - (File: `program/src/processor.rs`, `program/src/instruction.rs`)

### Summary
`Processor::process_deposit` relies on `DepositInstruction.other_amount_min` as the only lower-bound slippage protection for the "counter-side" token that is computed by the program from the pool's live ratio. This field is an `Option<u64>` that is only populated when the instruction data happens to contain the extra 8 bytes; when it is `None`, no lower-bound check is performed at all, so a depositor has no protection against the pool ratio being manipulated in their favor-or-against by an attacker between transaction submission and execution.

### Finding Description
`DepositInstruction` carries `max_coin_amount`, `max_pc_amount`, `base_side`, and `other_amount_min: Option<u64>` [1](#0-0) . The unpacker only sets `other_amount_min` if there happen to be 8 extra bytes in the instruction data; otherwise it silently becomes `None` [2](#0-1) .

In `process_deposit`, when `base_side == 0` (deposit sized by coin), the program computes `deduct_pc_amount` from the *current* pool ratio and enforces only an upper bound (`deduct_pc_amount > deposit.max_pc_amount` → `ExceededSlippage`). The lower bound is enforced **only if `other_amount_min.is_some()`**: [3](#0-2) 

The symmetric `base_side == 1` branch has the identical pattern: an unconditional upper-bound check on `deduct_coin_amount` vs `max_coin_amount`, and a lower-bound check on `deduct_coin_amount` vs `other_amount_min` that is skipped entirely when `other_amount_min` is `None`: [4](#0-3) 

Because the "other side" amount and the resulting `mint_lp_amount` are both derived from the pool's instantaneous ratio/depth (`total_coin_without_take_pnl` / `total_pc_without_take_pnl`) at execution time, an attacker who can insert a swap immediately before the victim's deposit (front-running, e.g. via mempool/leader ordering or by bundling) can shift the pool ratio just enough to push `deduct_pc_amount` (or `deduct_coin_amount`) to the edge of, or outside, what the depositor considered acceptable — and if the depositor's client omitted `other_amount_min` (which the wire format explicitly allows), there is no revert to protect them. The attacker can then reverse the swap after the deposit lands, extracting the price-impact/fee difference at the depositor's expense while the depositor is left holding LP tokens that reflect a skewed contribution ratio.

This is the same bug class as the referenced Olympus report: a slippage-protection parameter exists in the interface and is *documented* as protecting against front-running, but the on-chain enforcement is conditional/optional rather than mandatory, so it can be bypassed simply by not supplying it (whether by an unaware integrator or a malicious client crafting the instruction data directly, since the instruction is unpacked straight from raw bytes with no requirement that the field be present) [2](#0-1) .

### Impact Explanation
A depositor who submits (or whose wallet/integration submits) a `Deposit` instruction without `other_amount_min` has no guarantee on the value/ratio of tokens actually deducted beyond the single explicit upper bound they chose. An attacker capable of ordering a swap immediately before the deposit can manipulate the effective deposit ratio and capture value from the depositor via the subsequent LP mint and reversal trade. This is a fund-loss risk to LPs, not merely a UX inconvenience, since real caller funds are deducted based on an on-chain-manipulable ratio with no protocol-enforced floor.

### Likelihood Explanation
`other_amount_min` is optional by design in both the instruction struct and the wire encoding/decoding logic, so any deposit built without it (which the README's example CLI usage shows is a normal, selectable configuration — `another_min_limit: false`) is unprotected by default [5](#0-4) . Any user able to submit a transaction with attacker-chosen instruction data and account ordering ahead of a pending deposit (a swap instruction, which is fully permissionless) can trigger the manipulation; no privileged access is required.

### Recommendation
Make the counter-side slippage bound mandatory rather than optional — require `other_amount_min` (or equivalent min-out/min-lp parameter) to always be present and enforced in `process_deposit`, and/or add an explicit `min_lp_amount` check on `mint_lp_amount` so that the LP tokens minted are also bounded regardless of which side (`base_side`) is used for sizing the deposit.

### Proof of Concept
1. Attacker observes a pending `Deposit` transaction (base_side = 0, `max_coin_amount = C`, `max_pc_amount = M`, `other_amount_min = None`).
2. Attacker submits a swap transaction ahead of it that shifts the pool ratio so that `exchange_coin_to_pc(C)` now returns a `deduct_pc_amount` close to `M` (or, if optimizing to minimize the counter-side amount, a value far below the depositor's expectation) — either direction bypasses protection since the only enforced bound is the upper one and the lower one is absent.
3. The victim's deposit executes at `processor.rs:1200-1250`, minting `mint_lp_amount` proportional to the manipulated ratio instead of the ratio the depositor expected when signing.
4. Attacker reverses the initial swap, restoring the pool to its prior ratio and capturing the price-impact differential, effectively extracting value contributed by the victim's deposit.

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

**File:** program/src/instruction.rs (L355-371)
```rust
            3 => {
                let (max_coin_amount, rest) = Self::unpack_u64(rest)?;
                let (max_pc_amount, rest) = Self::unpack_u64(rest)?;
                let (base_side, rest) = Self::unpack_u64(rest)?;
                let other_amount_min = if rest.len() >= 8 {
                    let (other_amount_min, _rest) = Self::unpack_u64(rest)?;
                    Some(other_amount_min)
                } else {
                    None
                };
                Self::Deposit(DepositInstruction {
                    max_coin_amount,
                    max_pc_amount,
                    base_side,
                    other_amount_min,
                })
            }
```

**File:** program/src/processor.rs (L1200-1242)
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
```

**File:** program/src/processor.rs (L1251-1293)
```rust
        } else {
            // base pc
            deduct_coin_amount = invariant
                .exchange_pc_to_coin(deposit.max_pc_amount, RoundDirection::Ceiling)
                .ok_or(AmmError::CalculationExRateFailure)?;
            deduct_pc_amount = deposit.max_pc_amount;
            if deduct_coin_amount > deposit.max_coin_amount {
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
            // base pc, check other_amount_min if need
            if deposit.other_amount_min.is_some() {
                if deduct_coin_amount < deposit.other_amount_min.unwrap() {
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
```

**File:** README.md (L139-147)
```markdown
let subcmd = AmmCommands::Deposit {
    pool_id: Pubkey::from_str("The specified pool of the assets deposite to").unwrap(),
    deposit_token_coin: Some(Pubkey::from_str("The specified token coin of the user deposit").unwrap()),
    deposit_token_pc: Some(Pubkey::from_str("The specified token pc of the user deposit").unwrap()),
    recipient_token_lp: Some(Pubkey::from_str("The specified lp token of the user will receive").unwrap()),
    amount_specified: 100000u64,
    another_min_limit: false,
    base_coin: false,
};
```
