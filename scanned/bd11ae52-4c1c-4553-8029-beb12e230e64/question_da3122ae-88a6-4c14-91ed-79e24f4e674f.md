[File: 'solana/programs/bridge_token_factory/src/instructions/admin/initialize.rs -> Scope: High. Replayable, non-unique, or

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/admin/initialize.rs (L1-50)
```rust
use anchor_lang::prelude::*;

use crate::{
    constants::{AUTHORITY_SEED, CONFIG_SEED, SOL_VAULT_SEED, USED_NONCES_PER_ACCOUNT},
    state::{
        config::{Config, ConfigBumps, WormholeBumps},
        used_nonces::UsedNonces,
    },
};
use anchor_lang::system_program::{transfer, Transfer};
use wormhole_anchor_sdk::wormhole::{self, program::Wormhole};

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = payer,
        space = 8 + Config::INIT_SPACE,
        seeds = [CONFIG_SEED],
        bump,
    )]
    pub config: Account<'info, Config>,

    #[account(
        mut,
        seeds = [AUTHORITY_SEED],
        bump,
    )]
    pub authority: SystemAccount<'info>,

    #[account(
        mut,
        seeds = [SOL_VAULT_SEED],
        bump,
    )]
    pub sol_vault: SystemAccount<'info>,

    #[account(
        mut,
        seeds = [wormhole::BridgeData::SEED_PREFIX],
        bump,
        seeds::program = wormhole_program.key,
    )]
    /// Wormhole bridge data account (a.k.a. its config).
    /// [`wormhole::post_message`] requires this account be mutable.
    pub wormhole_bridge: Box<Account<'info, wormhole::BridgeData>>,

    #[account(
        mut,
        seeds = [wormhole::FeeCollector::SEED_PREFIX],
```

**File:** solana/programs/bridge_token_factory/src/state/used_nonces.rs (L1-112)
```rust
use anchor_lang::prelude::*;
use anchor_lang::system_program::transfer;
use anchor_lang::system_program::Transfer;
#[cfg(not(feature =
