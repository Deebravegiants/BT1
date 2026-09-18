## Title
Withdraw's slippage protection (`min_coin_amount`/`min_pc_amount`) is optional and can be bypassed, enabling sandwich attacks against LPs - (File: `program/src/processor.rs`)

### Summary
The `Withdraw` instruction accepts optional minimum-out parameters that are meant to protect a liquidity provider from price manipulation between transaction submission and execution. Because these parameters are `Option<u64>` and the enforcement code only runs the slippage check `if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some()`, a withdrawal submitted without these bounds (or with a client default of "no slippage limit") executes unconditionally at whatever ratio the pool holds at execution time, regardless of how much that ratio has been manipulated by an attacker's preceding swap.

### Finding Description
`WithdrawInstruction` carries `min_coin_amount: Option<u64>` and `min_pc_amount: Option<u64>`, and the on-chain unpacker only populates both fields when the caller sends 16 extra bytes; otherwise both remain `None`: [1](#0-0) 

Inside `process_withdraw`, the `coin_amount`/`pc_amount` a user receives are computed from the pool's current vault balances (`total_coin_without_take_pnl`, `total_pc_without_take_pnl`) proportional to the LP amount being burned, via `InvariantPool::exchange_pool_to_token`: [2](#0-1) 

The slippage check is then only exercised when both minimums were supplied: [3](#0-2) 

If either field is `None` (which is the default outcome whenever a caller — including the reference CLI's `slippage_limit: false` path — omits the extra 16 bytes) the branch is skipped entirely and the withdrawal proceeds with no floor on `coin_amount`/`pc_amount`. The README documents this exact optional flag on the CLI's `Withdraw` command (`slippage_limit: false`), confirming it is a normal, reachable client configuration, not an edge case: [4](#0-3) 

Because the pool's vault ratio can be freely and permissionlessly shifted by any unprivileged swapper via `SwapBaseIn`/`SwapBaseOut`/`SwapBaseInV2`/`SwapBaseOutV2` in the same block (single-transaction bundle or back-to-back transactions), an attacker can:
1. Observe a pending `Withdraw` transaction (or simply time the attack when a withdrawal is expected).
2. Execute a large swap against the pool to skew `amm_coin_vault.amount` / `amm_pc_vault.amount` in one direction.
3. Let the victim's `Withdraw` execute at the skewed ratio, receiving a value-imbalanced pair of tokens (much more of the depressed asset, much less of the appreciated one) instead of the expected pro-rata amounts.
4. Reverse the swap afterward to restore the price and capture the value difference (classic sandwich), or simply extract value if a third-party's swap happens to move price unfavorably before the withdrawal lands.

This mirrors the reported Vultisig `ILOPool.claim` bug class: an operation that computes payout amounts from a manipulable on-chain price/ratio but whose slippage floor is not mandatorily enforced.

### Impact Explanation
A withdrawing LP can receive coin/pc amounts far below fair value if the vault ratio is manipulated immediately before their withdrawal executes and they (or the client they used) did not supply `min_coin_amount`/`min_pc_amount`. This is a realizable value-extraction/impermanent-loss vector reachable by any unprivileged party who can submit swap transactions against the pool — no privileged signer or off-chain component is required.

### Likelihood Explanation
Likelihood is moderate: exploitation requires the victim's withdrawal to omit the optional minimums (a state explicitly supported and documented via `slippage_limit: false`), and requires an attacker to have sufficient capital/liquidity access to meaningfully move the pool's vault ratio within the same slot/transaction ordering window, similar to typical sandwich-attack economics on AMMs. As with the original finding, the LP-owner is generally only harming themselves by choosing to omit slippage protection, which reduces — but does not eliminate — real-world severity, since many wallets/integrators may default to no-slippage-limit for withdrawals.

### Recommendation
Make the minimum-out check mandatory (i.e., require `min_coin_amount` and `min_pc_amount` to always be supplied and enforced) rather than optional, so that `process_withdraw` cannot silently skip the slippage check documented as available in `AmmError::ExceededSlippage`.

### Proof of Concept
1. Attacker monitors mempool/upcoming instructions for a `Withdraw` instruction whose packed data omits the 16 trailing bytes for `min_coin_amount`/`min_pc_amount` (`program/src/instruction.rs` lines 372-386 show this is the standard "short form" encoding).
2. Attacker submits a large `SwapBaseIn`/`SwapBaseOut` against the same AMM immediately before the victim's withdraw lands, shifting `amm_coin_vault.amount`/`amm_pc_vault.amount`.
3. Victim's `process_withdraw` computes `coin_amount`/`pc_amount` off the now-skewed vault totals (`program/src/processor.rs` lines 1719-1761), and since `withdraw.min_coin_amount`/`min_pc_amount` are `None`, the check at lines 1779-1786 is bypassed, and the transfer/burn proceeds at the skewed ratio.
4. Attacker reverses the swap afterward, realizing a profit at the withdrawing LP's expense.

### Citations

**File:** program/src/instruction.rs (L372-386)
```rust
            4 => {
                let (amount, rest) = Self::unpack_u64(rest)?;
                let (min_coin_amount, min_pc_amount) = if rest.len() >= 16 {
                    let (min_coin_amount, rest) = Self::unpack_u64(rest)?;
                    let (min_pc_amount, _rest) = Self::unpack_u64(rest)?;
                    (Some(min_coin_amount), Some(min_pc_amount))
                } else {
                    (None, None)
                };
                Self::Withdraw(WithdrawInstruction {
                    amount,
                    min_coin_amount,
                    min_pc_amount,
                })
            }
```

**File:** program/src/processor.rs (L1719-1761)
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
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
        }

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

**File:** README.md (L153-164)
```markdown
4. withdraw assets from amm pool
```rust
// build withdraw instruction
let subcmd = AmmCommands::Withdraw {
    pool_id: Pubkey::from_str("The specified pool of the assets withdraw from").unwrap(),
    withdraw_token_lp: Some(Pubkey::from_str("The specified lp token of the user withdraw").unwrap()),
    recipient_token_coin: Some(Pubkey::from_str("The specified token coin of the user will receive").unwrap()),
    recipient_token_pc: Some(Pubkey::from_str("The specified token pc of the user will receive").unwrap()),
    input_lp_amount: 100000u64,
    slippage_limit: false,
};
let instruction = amm_cli::process_amm_commands(subcmd, &config).unwrap();
```
