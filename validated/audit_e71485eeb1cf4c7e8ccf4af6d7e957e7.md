### Title
Lack of emergency withdrawal path when pool status is set to `Disabled` permanently freezes LP holder funds - (File: `program/src/state.rs`, `program/src/processor.rs`)

### Summary
Raydium AMM's `Withdraw` instruction is gated by `AmmStatus::withdraw_permission()`, which returns `false` for the `Disabled` (and `Uninitialized`) status. Once a pool's status is set to `Disabled`, LP token holders have no instruction path in the program to redeem their LP tokens for the underlying coin/pc tokens, permanently trapping their liquidity in the vaults.

### Finding Description
`process_withdraw` explicitly checks the pool status before allowing any withdrawal: [1](#0-0) 

The permission table shows that only `Disabled` and `Uninitialized` block withdrawal, while every other status (`Initialized`, `WithdrawOnly`, `LiquidityOnly`, `OrderBookOnly`, `SwapOnly`, `WaitingTrade`) permits it: [2](#0-1) 

Status is set purely by `process_set_params` (`AmmParams::Status`), which validates the new value only against `AmmStatus::valid_status`, allowing any value from `Initialized` through `WaitingTrade`, including `Disabled` (2): [3](#0-2) [4](#0-3) 

No other instruction in the program allows an LP holder to burn LP tokens and reclaim their share of `coin_vault`/`pc_vault` once `withdraw_permission()` is `false`. The only other vault-draining instruction, `process_withdrawpnl`, is restricted to the protocol's `pnl_owner`/`amm_owner` and only pays out accumulated PnL, not user LP principal: [5](#0-4) 

There is no `EmergencyWithdraw` or equivalent instruction anywhere in the codebase (confirmed by searching for "emergency" across the repo), mirroring exactly the gap described in the original `BLVaultLido` report: a state ("inactive"/"paused") exists that blocks the normal withdraw path, and no fallback exists for users to reclaim principal.

### Impact Explanation
If the pool status is ever set to `Disabled` — whether intentionally (e.g., admin pausing a pool due to a discovered issue) or accidentally — every LP holder's deposited coin and pc tokens become permanently unrecoverable through the program, since the sole instruction that can move funds out to LPs (`Withdraw`) is hard-gated by `withdraw_permission()`. This is a permanent freezing of user/LP funds, matching the "Medium" impact bar (permanent freezing of user or LP funds).

### Likelihood Explanation
Reaching the frozen state requires the `SetParams` admin instruction to move status to `Disabled`, which is an expected operational lever already present in the deployed program (used, e.g., to pause a compromised or paused pool) — the same operational scenario the original report contemplates ("in the event of the vault becoming inactive, by decision of admin or because there is a critical issue"). Once that state is reached, every subsequent LP `Withdraw` transaction from any unprivileged holder — attacker-chosen accounts, standard instruction data — deterministically fails at the status check, with no code path available to recover funds.

### Recommendation
Add an "emergency withdraw" style code path (or relax `withdraw_permission()` for `Disabled` pools) that lets LP token holders burn their LP tokens and redeem a pro-rata share of `coin_vault`/`pc_vault` even while the pool is `Disabled`, mirroring the recommendation in the source report. At minimum, `Disabled` should preserve `withdraw_permission() == true` (as `WithdrawOnly` already does) so admins can halt swaps/deposits without trapping LP principal.

### Proof of Concept
1. Admin calls `SetParams` with `param = AmmParams::Status` and `value = AmmStatus::Disabled.into_u64()` (2) on an active pool — allowed per `process_set_params` validation at `program/src/processor.rs:2665-2676`.
2. Any LP holder submits a normal `Withdraw` instruction with their LP tokens.
3. `process_withdraw` calls `AmmStatus::from_u64(amm.status).withdraw_permission()`, which returns `false` for `Disabled`, and the instruction fails with `AmmError::InvalidStatus` (`program/src/processor.rs:1652-1654`).
4. No other program instruction (including `WithdrawPnl`, restricted to `pnl_owner`/`amm_owner`) allows the LP holder to redeem their share — funds remain in `coin_vault`/`pc_vault` indefinitely.

### Citations

**File:** program/src/processor.rs (L1406-1411)
```rust
        if !pnl_owner_info.is_signer
            || (*pnl_owner_info.key != config_feature::amm_owner::ID
                && *pnl_owner_info.key != amm_config.pnl_owner)
        {
            return Err(AmmError::InvalidSignAccount.into());
        }
```

**File:** program/src/processor.rs (L1652-1654)
```rust
        if !AmmStatus::from_u64(amm.status).withdraw_permission() {
            return Err(AmmError::InvalidStatus.into());
        }
```

**File:** program/src/processor.rs (L2665-2676)
```rust
            AmmParams::Status => {
                match setparams.value {
                    Some(status) => {
                        if AmmStatus::valid_status(status) {
                            amm.status = status as u64;
                        } else {
                            return Err(AmmError::InvalidInput.into());
                        }
                    }
                    None => return Err(AmmError::InvalidInput.into()),
                };
            }
```

**File:** program/src/state.rs (L263-268)
```rust
    pub fn valid_status(status: u64) -> bool {
        match status {
            1u64 | 2u64 | 3u64 | 4u64 | 5u64 | 6u64 | 7u64 => return true,
            _ => return false,
        }
    }
```

**File:** program/src/state.rs (L283-294)
```rust
    pub fn withdraw_permission(&self) -> bool {
        match self {
            AmmStatus::Uninitialized => false,
            AmmStatus::Initialized => true,
            AmmStatus::Disabled => false,
            AmmStatus::WithdrawOnly => true,
            AmmStatus::LiquidityOnly => true,
            AmmStatus::OrderBookOnly => true,
            AmmStatus::SwapOnly => true,
            AmmStatus::WaitingTrade => true,
        }
    }
```
