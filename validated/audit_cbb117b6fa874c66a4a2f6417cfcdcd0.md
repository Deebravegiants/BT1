No vulnerability found for this question.

The reported issue concerns a lending protocol (`Cooler.sol`) where borrowers set a loan `duration` param with no maximum bound, preventing lenders from ever liquidating. Raydium AMM has no borrowing/lending, loan origination, or duration/expiry mechanic in its scope. The only analogous time-based field is `pool_open_time` used in `AmmStatus::WaitingTrade` gating for swaps, which is set once at pool initialization (via `InitializeInstruction`/`InitializeInstruction2`) or by the privileged `amm_owner` via `AmmParams::SetOpenTime` in `process_set_params`, not by an arbitrary unprivileged party analogous to a borrower choosing an unbounded duration against a counterparty's funds [1](#0-0) . This time field only affects when swaps become permitted, and unlike the Cooler loan-expiry issue there is no mechanism where one party locks up another's assets for an attacker-chosen unbounded time period [2](#0-1) . No unprivileged, single-transaction path (Initialize2, Deposit, Withdraw, or the swap instructions) reproduces the "unbounded lock/expiry causing freezing of counterparty funds" bug class.

### Citations

**File:** program/src/processor.rs (L2696-2704)
```rust
            }
            AmmParams::SetOpenTime => {
                match setparams.value {
                    Some(time) => {
                        amm.state_data.pool_open_time = time as u64;
                    }
                    None => return Err(AmmError::InvalidInput.into()),
                };
            }
```

**File:** program/src/state.rs (L221-235)
```rust
#[repr(u64)]
pub enum AmmStatus {
    Uninitialized = 0u64,
    Initialized = 1u64,
    Disabled = 2u64,
    WithdrawOnly = 3u64,
    // pool only can add or remove liquidity, can't swap and plan orders
    LiquidityOnly = 4u64,
    // pool only can add or remove liquidity and plan orders, can't swap
    OrderBookOnly = 5u64,
    // pool only can add or remove liquidity and swap, can't plan orders
    SwapOnly = 6u64,
    // pool status after created and will auto update to SwapOnly during swap after open_time
    WaitingTrade = 7u64,
}
```
