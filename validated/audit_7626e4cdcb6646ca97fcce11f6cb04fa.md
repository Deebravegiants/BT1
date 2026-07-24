The code confirms the vulnerability. Let me trace the exact path:

**`log_metadata.rs`**: The `vault` account uses `init_if_needed` with no NEAR-confirmation gate. The only constraint on `mint` is that the bridge authority is NOT the mint authority (i.e., it's a native/external token). Any unprivileged user can call this for any arbitrary SPL token. [1](#0-0) 

**`init_transfer.rs`**: The code explicitly treats vault existence as "proof of token registration" — but vault creation via `log_metadata` is entirely independent of NEAR-side confirmation. [2](#0-1) 

**NEAR side**: Token registration on NEAR requires someone to call `deploy_token` with a valid proof, and NEAR checks that the emitter address matches a known factory. This is not automatic — if the proof is never submitted, or NEAR is paused, the token is never registered. [3](#0-2) 

There is no cancel/refund instruction in the admin or user instruction set.


`finalize_transfer` (the only vault-release path) requires a signed payload originating from NEAR — which will never arrive for an unregistered token. [4](#0-3) 

---

### Title
Vault-Existence Used as False Proof of NEAR Registration Enables Permanent Fund Lock — (`solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs`)

### Summary
`log_metadata` creates a vault PDA via `init_if_needed` for any arbitrary SPL token without any on-chain confirmation that NEAR has registered the token. `init_transfer` then uses vault existence as its sole "proof of token registration." If NEAR never processes the `LogMetadata` Wormhole message (e.g., proof never submitted, NEAR paused, or emitter not whitelisted), tokens transferred via `init_transfer` are permanently locked in the vault with no redemption path.

### Finding Description
The `LogMetadata` account struct unconditionally creates the vault PDA on first call:

```rust
// log_metadata.rs:51-62
#[account(
    init_if_needed,
    payer = common.payer,
    token::mint = mint,
    token::authority = authority,
    seeds = [VAULT_SEED, mint.key().as_ref()],
    bump,
    token::token_program = token_program,
)]
pub vault: Box<InterfaceAccount<'info, TokenAccount>>,
```

No on-chain state records whether NEAR has confirmed registration. `InitTransfer` then branches solely on vault existence:

```rust
// init_transfer.rs:88-89
if let Some(vault) = &self.vault {
    // Native version. We have a proof of token registration by vault existence
```

The comment itself documents the broken invariant: vault existence is not equivalent to NEAR-side registration. The vault is created by `log_metadata` on Solana; NEAR registration requires a separate `deploy_token` call with a valid Wormhole proof. These two steps are decoupled with no enforcement.

The only path to release tokens from the vault is `finalize_transfer`, which requires a signed `FinalizeTransferPayload` originating from NEAR. Since NEAR never registered the token, it will never emit such a payload, making the lock permanent.

### Impact Explanation
**Critical — Irreversible fund lock.** Any user who calls `init_transfer` for a token whose `log_metadata` Wormhole message was not processed by NEAR loses their tokens permanently. The vault balance increases, no NEAR credit is issued, and no on-chain recovery path exists.

### Likelihood Explanation
The gap between vault creation (Solana-local, instant) and NEAR registration (requires off-chain relaying + `deploy_token` call) is a real operational window. Scenarios that trigger it:
- Wormhole relayer does not relay the VAA (e.g., fee not paid, relayer outage)
- Nobody calls `deploy_token` on NEAR with the proof
- NEAR contract is paused at the time of relaying
- The Solana factory address is not yet registered in NEAR's `factories` map

A user who calls `init_transfer` during this window — or for a token that NEAR will never register — permanently loses funds.

### Recommendation
Add an explicit on-chain registration flag (e.g., a PDA account `[REGISTERED_SEED, mint.key()]`) that is only created by a NEAR-originated `deploy_token` callback relayed back to Solana. Gate `init_transfer`'s native path on this flag rather than on vault existence. Alternatively, implement a cancellation/refund instruction that allows the original sender to reclaim tokens from the vault if a configurable timeout elapses without a corresponding `finalize_transfer`.

### Proof of Concept
1. Create arbitrary SPL token `T` (no bridge authority as mint authority).
2. Call `log_metadata(T)` → vault PDA `[VAULT_SEED, T]` is created; Wormhole message emitted.
3. Do NOT relay the VAA to NEAR (or let NEAR reject it). Token `T` is unregistered on NEAR.
4. Call `init_transfer(T, amount=X)` → vault exists → `transfer_checked` moves `X` tokens from user ATA to vault. Wormhole `InitTransfer` message emitted.
5. NEAR receives `InitTransfer` proof for unregistered token → rejects it. No credit issued.
6. Assert: vault balance = `X`; user ATA balance decreased by `X`; no NEAR-side credit; no `finalize_transfer` possible.

Tokens in vault are permanently unrecoverable.

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L41-62)
```rust
    #[account(
        constraint = !mint.mint_authority.contains(authority.key),
        mint::token_program = token_program,
    )]
    pub mint: Box<InterfaceAccount<'info, Mint>>,

    /// CHECK: may be unitialized
    pub metadata: Option<UncheckedAccount<'info>>,

    #[account(
        init_if_needed,
        payer = common.payer,
        token::mint = mint,
        token::authority = authority,
        seeds = [
            VAULT_SEED,
            mint.key().as_ref(),
        ],
        bump,
        token::token_program = token_program,
    )]
    pub vault: Box<InterfaceAccount<'info, TokenAccount>>,
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs (L88-102)
```rust
        if let Some(vault) = &self.vault {
            // Native version. We have a proof of token registration by vault existence
            transfer_checked(
                CpiContext::new(
                    self.token_program.to_account_info(),
                    TransferChecked {
                        from: self.from.to_account_info(),
                        to: vault.to_account_info(),
                        authority: self.user.to_account_info(),
                        mint: self.mint.to_account_info(),
                    },
                ),
                payload.amount.try_into().map_err(|_| error!(ErrorCode::InvalidArgs))?,
                self.mint.decimals,
            )?;
```

**File:** near/omni-bridge/src/lib.rs (L1159-1167)
```rust
        let Ok(ProverResult::LogMetadata(metadata)) = call_result else {
            env::panic_str(BridgeError::InvalidProofMessage.to_string().as_str());
        };

        let chain = metadata.emitter_address.get_chain();
        require!(
            self.factories.get(&chain) == Some(metadata.emitter_address),
            BridgeError::UnknownFactory.as_ref()
        );
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer.rs (L101-116)
```rust
        if let Some(vault) = &self.vault {
            // Native version. We have a proof of token registration by vault existence
            transfer_checked(
                CpiContext::new_with_signer(
                    self.token_program.to_account_info(),
                    TransferChecked {
                        from: vault.to_account_info(),
                        to: self.token_account.to_account_info(),
                        authority: self.authority.to_account_info(),
                        mint: self.mint.to_account_info(),
                    },
                    &[&[AUTHORITY_SEED, &[self.config.bumps.authority]]],
                ),
                data.amount.try_into().map_err(|_| error!(ErrorCode::AmountOverflow))?,
                self.mint.decimals,
            )?;
```
