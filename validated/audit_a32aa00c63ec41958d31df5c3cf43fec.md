### Title
Native Fee Permanently Locked in `sol_vault` PDA With No Withdrawal Mechanism — (File: `solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs`, `init_transfer_sol.rs`)

### Summary
Every call to `init_transfer` and `init_transfer_sol` transfers a user-supplied `native_fee` in SOL into the `sol_vault` PDA. No instruction in the program allows anyone — admin or otherwise — to withdraw those accumulated lamports. The fees are permanently locked inside a program-controlled PDA.

### Finding Description
`init_transfer` collects `native_fee` from the user and sends it to the `sol_vault` PDA: [1](#0-0) 

`init_transfer_sol` sends `native_fee + amount` to the same `sol_vault`: [2](#0-1) 

`finalize_transfer_sol` only releases the bridged `amount` back to the recipient — the `native_fee` portion is never touched: [3](#0-2) 

`sol_vault` is a PDA seeded with `SOL_VAULT_SEED`, meaning only the program itself can sign for it: [4](#0-3) 

The complete set of admin instructions — `initialize`, `change_config`, `pause`, `update_metadata` — contains no fee-withdrawal instruction: [5](#0-4) 

The complete set of user instructions likewise contains no mechanism to drain accumulated fees from `sol_vault`: [6](#0-5) 

The program's top-level `lib.rs` confirms the exhaustive instruction list — there is no `withdraw_fees` or equivalent entry point: [7](#0-6) 

### Impact Explanation
Every lamport paid as `native_fee` through `init_transfer` or `init_transfer_sol` is irrecoverably locked inside the `sol_vault` PDA. Over the protocol's lifetime this accumulates into permanently unclaimable protocol value. This matches the allowed impact: *"Irreversible fund lock… permanently unclaimable user or protocol value in bridge… fee… flows."*

### Likelihood Explanation
`init_transfer` and `init_transfer_sol` are the primary public bridge entry points. Any user who supplies a non-zero `native_fee` (which the protocol is designed to accept) triggers the lock. No special role or condition is required — it is reachable by any unprivileged caller on every bridging transaction.

### Recommendation
Add an admin-gated `withdraw_fees` instruction that uses a PDA signer for `sol_vault` to transfer accumulated lamports to a designated treasury address, analogous to the fix applied in the referenced `early-purchase` program (`withdraw_funds` instruction). The instruction should be restricted to the `admin` stored in `Config` and should transfer only the surplus above the rent-exempt minimum to avoid closing the account.

### Proof of Concept
1. User calls `init_transfer` with `native_fee = 1_000_000` lamports (0.001 SOL) and any valid SPL token amount.
2. The program executes the transfer at `init_transfer.rs:76–86`, moving 1_000_000 lamports into `sol_vault`.
3. The cross-chain message is posted; the NEAR side finalizes the token transfer normally.
4. No instruction exists to recover the 1_000_000 lamports from `sol_vault`.
5. Repeated over thousands of bridge transactions, the locked SOL grows without bound and is permanently inaccessible to the protocol.

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs (L75-86)
```rust
        if payload.native_fee > 0 {
            transfer(
                CpiContext::new(
                    self.common.system_program.to_account_info(),
                    Transfer {
                        from: self.user.to_account_info(),
                        to: self.sol_vault.to_account_info(),
                    },
                ),
                payload.native_fee,
            )?;
        }
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/init_transfer_sol.rs (L39-53)
```rust
        transfer(
            CpiContext::new(
                self.common.system_program.to_account_info(),
                Transfer {
                    from: self.user.to_account_info(),
                    to: self.sol_vault.to_account_info(),
                },
            ),
            payload
                .native_fee
                .checked_add(
                    payload.amount.try_into().map_err(|_| error!(ErrorCode::InvalidArgs))?,
                )
                .ok_or_else(|| error!(ErrorCode::InvalidArgs))?,
        )?;
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer_sol.rs (L79-89)
```rust
        transfer(
            CpiContext::new_with_signer(
                self.common.system_program.to_account_info(),
                Transfer {
                    from: self.sol_vault.to_account_info(),
                    to: self.recipient.to_account_info(),
                },
                &[&[SOL_VAULT_SEED, &[self.config.bumps.sol_vault]]],
            ),
            data.amount.try_into().map_err(|_| error!(ErrorCode::AmountOverflow))?,
        )?;
```

**File:** solana/programs/bridge_token_factory/src/constants.rs (L13-14)
```rust
pub const SOL_VAULT_SEED: &[u8] = b"sol_vault";

```

**File:** solana/programs/bridge_token_factory/src/instructions/admin/mod.rs (L1-8)
```rust
pub mod change_config;
pub mod initialize;
pub mod pause;
pub mod update_metadata;

pub use change_config::*;
pub use initialize::*;
pub use pause::*;
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/mod.rs (L1-11)
```rust
pub mod deploy_token;
pub mod finalize_transfer;
pub mod finalize_transfer_sol;
pub mod get_version;
pub mod init_transfer;
pub mod init_transfer_sol;
pub mod log_metadata;

pub use deploy_token::*;
pub use finalize_transfer::*;
pub use finalize_transfer_sol::*;
```

**File:** solana/programs/bridge_token_factory/src/lib.rs (L1-10)
```rust
use anchor_lang::prelude::*;
use instructions::{
    ChangeConfig, DeployToken, FinalizeTransfer, FinalizeTransferSol, GetVersion, InitTransfer,
    InitTransferSol, Initialize, LogMetadata, Pause, UpdateMetadata,
    __client_accounts_change_config, __client_accounts_deploy_token,
    __client_accounts_finalize_transfer, __client_accounts_finalize_transfer_sol,
    __client_accounts_get_version, __client_accounts_init_transfer,
    __client_accounts_init_transfer_sol, __client_accounts_initialize,
    __client_accounts_log_metadata, __client_accounts_pause, __client_accounts_update_metadata,
};
```
