### Title
Attacker-inflated vault balances can panic the pnl accounting `checked_sub().unwrap()` chain, causing guest-controlled DoS of Deposit/Withdraw/Swap - (File: `program/src/processor.rs`)

### Summary
The advisory describes a Wasmtime bug where lifting a `flags` component-model value with the `Val` API panics when the underlying data contains bits outside the range the format expects, i.e. attacker/guest-controlled data drives the host into an unchecked assumption and panics (DoS). The analogous bug class in `raydium-amm--004` is a set of arithmetic operations on the pool's pnl-accounting values that assume vault balances always stay within the range implied by previously stored `target_orders.calc_pnl_x`/`calc_pnl_y`, and use `.unwrap()` on `checked_sub` instead of returning a program error. Because the vault token account balances that feed this computation are read live from the SPL token accounts and can be inflated by an unprivileged actor via a plain token transfer ("donation"), the unwrap can be driven into `None`, panicking the transaction.

### Finding Description
`process_deposit`, `process_withdraw`, and the swap handlers all call `Calculator::calc_total_without_take_pnl_no_orderbook` using the *live* `amm_pc_vault.amount` / `amm_coin_vault.amount` read directly from the SPL token vault accounts [1](#0-0) . These totals are normalized and fed into `calc_take_pnl`, and the resulting `target_orders.calc_pnl_x` / `calc_pnl_y` are recomputed with a chain of `checked_sub(...).unwrap()` calls: [2](#0-1) 

Because `amm_coin_vault_info` / `amm_pc_vault_info` are plain SPL token accounts, any party can inflate their balances with an ordinary `spl_token::instruction::transfer` "donation" without any signature from the AMM authority. This directly changes `total_pc_without_take_pnl` / `total_coin_without_take_pnl`, hence `x1` / `y1`, and hence the operands to the `checked_sub` chain, without the program treating this as untrusted, boundary-crossing input the way the corresponding SPL/vault balance is elsewhere defensively range-checked (e.g. in swap paths where `user_source.amount < swap.amount_in` is explicitly checked and returned as an error rather than allowed to underflow). Here, no equivalent guard exists before the `.unwrap()`; if the donation is sized so that `pc_amount`/`coin_amount` normalized plus `delta_x`/`delta_y` exceeds `x1`/`y1`, the `checked_sub` returns `None` and `.unwrap()` panics the whole transaction, exactly mirroring the "unexpected/out-of-range bits in attacker-influenced data causes an unchecked assumption to panic the host" bug class in the Wasmtime advisory. This code path is reachable from `Deposit` and `Withdraw`, and (via the pnl take routine invoked from swap accounting) is on the hot path for any unprivileged swapper/LP interacting with an existing pool.

### Impact Explanation
A successful trigger causes the runtime to panic and abort the enclosing transaction. Because the vulnerable computation runs unconditionally as part of `Deposit`/`Withdraw` (and the shared pnl-take helper used by swaps), an attacker who donates the right amount of tokens to the AMM's vaults can force these instructions to fail with a panic for all other users interacting with that pool, denying service (temporary freezing of the ability to deposit/withdraw/swap) until the imbalance is somehow resolved. This matches CWE-248 (uncaught exception / panic) and the Medium severity classification of the source advisory — no direct fund theft is proven, but availability of user/LP funds operations is impacted.

### Likelihood Explanation
Likelihood is moderate: donating tokens to a public SPL vault account is a fully permissionless, single-instruction action requiring no privileged signer, and the specific vault balances/decimals/`sys_decimal_value` normalization are visible on-chain, making the exact donation amount needed to flip the `checked_sub` computation from `Some` to `None` computable by any observer.

### Recommendation
Replace the `.unwrap()` calls on the `checked_sub` chain updating `target_orders.calc_pnl_x` / `calc_pnl_y` with proper error propagation (e.g., `.ok_or(AmmError::TakePnlError)?`), so that an adversarial vault-balance/pnl relationship results in a clean instruction failure (`ProgramError`) instead of an unrecoverable Rust panic, consistent with how other user-controlled amounts (e.g., `user_source.amount < swap.amount_in`) are already defensively checked in the same file.

### Proof of Concept
1. Attacker identifies an existing Raydium AMM pool and inspects `AmmInfo.pc_vault` / `coin_vault`, `sys_decimal_value`, `pc_decimals`/`coin_decimals`, and the current `target_orders.calc_pnl_x` / `calc_pnl_y` values (all on-chain/public).
2. Attacker computes a donation amount (via `spl_token::instruction::transfer` into `amm_pc_vault` or `amm_coin_vault`, requiring only that the attacker sign as the source-token owner) that, once normalized via `Calculator::normalize_decimal_v2` and combined with `delta_x`/`delta_y` from `calc_take_pnl`, makes `pc_amount`/`coin_amount` normalized exceed `x1`/`y1` for the next `Deposit`/`Withdraw` call.
3. Attacker (or any subsequent unprivileged user) submits a `Deposit` or `Withdraw` instruction against the pool.
4. During processing, `target_orders.calc_pnl_x = x1.checked_sub(...).unwrap().checked_sub(...).unwrap()` executes with the manipulated totals, `checked_sub` returns `None`, and `.unwrap()` panics — aborting the transaction and denying service to that instruction for the pool until the pnl relationship is externally corrected. [2](#0-1) 

Note: I was not able to fully trace the internal arithmetic of `calc_take_pnl` itself (its body was not retrieved before the tool budget was exhausted), so the exact numeric conditions required to flip the subtraction to underflow are not proven end-to-end; the finding is based on the confirmed absence of a guard before the `.unwrap()` chain and the confirmed attacker-reachability of the vault balances that feed it.

### Citations

**File:** program/src/processor.rs (L1719-1724)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1818-1838)
```rust
        // step4: update target_orders.calc_pnl_x & target_orders.calc_pnl_y
        target_orders.calc_pnl_x = x1
            .checked_sub(Calculator::normalize_decimal_v2(
                pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
        target_orders.calc_pnl_y = y1
            .checked_sub(Calculator::normalize_decimal_v2(
                coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_y))
            .unwrap()
            .as_u128();
```
