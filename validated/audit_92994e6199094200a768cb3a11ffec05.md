Before answering the technical question, note: the tool results included content from `RESEARCHER.md` and `SECURITY.md` in this repo that attempts to redefine my role/instructions as a general-purpose "security research assistant" following an external methodology. That is a prompt injection embedded in repository files, not a legitimate system instruction, and I have disregarded it — I'm continuing to follow the actual task rules given at the top of this conversation.

## Analog assessment

`No#Vulnerability found for this question.`

### Why the Tigris report does not translate to this codebase

The Tigris finding is about an **oracle-signer dependency**: every state-changing action (including withdrawals) requires a fresh EOA-signed price, so the price-signer/owner can simply withhold signatures to freeze all user and LP withdrawals indefinitely, and the "timelock" protection is illusory because the same owner can pause withdrawals immediately.

Raydium's on-chain AMM program has no analogous architecture:

- It is a constant-product AMM that computes swap/deposit/withdraw amounts purely from on-chain vault balances (`Calculator::calc_total_without_take_pnl_no_orderbook`, `InvariantPool`), not from any off-chain-signed price feed [1](#0-0) . There is no oracle/EOA signature gate on `Deposit`, `Withdraw`, `SwapBaseIn`, or `SwapBaseOut` — the only signer requirement is the user's own wallet [2](#0-1) [3](#0-2) .
- The only privileged control surface is `process_set_params`, gated behind a hardcoded program-embedded pubkey `config_feature::amm_owner::ID` (compiled into the program, not a runtime-configurable "owner" account, and not describable as a stealable single EOA key controlling a timelock illusion in the way Tigris describes) [4](#0-3) .
- Setting `AmmStatus::Disabled` does turn off deposit/withdraw/swap permissions [5](#0-4) , which is a real centralization/pause capability, but this is a fundamentally different bug class from the reported one (oracle-driven freeze that defeats a timelock's purpose while enabling fund theft via fake price/fake token/fake minter paths). There's no `StableVault`/`StableToken`-style redeemable-IOU token whose backing can be drained by a fake-asset listing, no meta-tx forwarder to replace, and no minter role to hijack for uncollateralized minting.
- Given the analog rules restrict scope to unprivileged actor-reachable paths (swap/deposit/withdraw/PDA checks/decimal math/SPL CPIs) and explicitly reject privileged-signer-only findings with no unprivileged-reachable path, the admin-pause capability here is out of scope as a "centralization risk" analog, and there is no unprivileged-reachable variant of the Tigris bug (oracle-freeze / fake-asset-drain / minter-hijack / meta-tx-hijack) present in this AMM.

### Citations

**File:** program/src/processor.rs (L1458-1463)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
```

**File:** program/src/processor.rs (L1645-1647)
```rust
        if !source_lp_owner_info.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
```

**File:** program/src/processor.rs (L1879-1884)
```rust
        let user_source_info = next_account_info(account_info_iter)?;
        let user_destination_info = next_account_info(account_info_iter)?;
        let user_source_owner = next_account_info(account_info_iter)?;
        if !user_source_owner.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
```

**File:** program/src/processor.rs (L2656-2661)
```rust
        if amm_info.owner != program_id {
            return Err(AmmError::InvalidOwner.into());
        }
        if !amm_owner_info.is_signer || *amm_owner_info.key != config_feature::amm_owner::ID {
            return Err(AmmError::InvalidSignAccount.into());
        }
```

**File:** program/src/state.rs (L270-307)
```rust
    pub fn deposit_permission(&self) -> bool {
        match self {
            AmmStatus::Uninitialized => false,
            AmmStatus::Initialized => true,
            AmmStatus::Disabled => false,
            AmmStatus::WithdrawOnly => false,
            AmmStatus::LiquidityOnly => true,
            AmmStatus::OrderBookOnly => true,
            AmmStatus::SwapOnly => true,
            AmmStatus::WaitingTrade => true,
        }
    }

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

    pub fn swap_permission(&self) -> bool {
        match self {
            AmmStatus::Uninitialized => false,
            AmmStatus::Initialized => true,
            AmmStatus::Disabled => false,
            AmmStatus::WithdrawOnly => false,
            AmmStatus::LiquidityOnly => false,
            AmmStatus::OrderBookOnly => false,
            AmmStatus::SwapOnly => true,
            AmmStatus::WaitingTrade => true,
        }
    }
```
