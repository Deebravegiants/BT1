### Title
Attacker Can Front-Run `finalize_transfer` With a Fake Mint to Permanently Lock User Funds - (File: `solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer.rs`)

### Summary
The Solana `FinalizeTransfer` instruction does not validate that the `mint` account passed by the caller matches the token address in the signed Wormhole payload. An unprivileged attacker can observe a legitimate Wormhole VAA for a NEAR→Solana transfer, create a fake SPL mint with the bridge authority PDA as its mint authority, and front-run the legitimate `finalize_transfer` call using the same VAA but their fake mint. The destination nonce is consumed, the legitimate finalization can never execute, and the user's tokens locked on NEAR are permanently unclaimable.

### Finding Description

In `finalize_transfer.rs`, the `mint` account is constrained only to be a valid SPL mint with the correct token program: [1](#0-0) 

There is no Anchor constraint binding `mint.key()` to any token address field inside `data.payload` (the Wormhole-verified `FinalizeTransferPayload`). For the bridged-token path (no vault), the only guard is: [2](#0-1) 

The bridge authority PDA address is deterministic and publicly derivable from the `AUTHORITY_SEED`. Any actor can create a standard SPL mint and set that PDA as the mint authority before calling `finalize_transfer`. The program's own comment acknowledges this possibility but incorrectly assumes NEAR will simply ignore the result:

> *"May be a fake token with our authority set but it will be ignored on the near side"*

The critical flaw is that the destination nonce is consumed unconditionally before the mint check: [3](#0-2) 

Once the nonce is marked used, the `UsedNonces` bitmap permanently blocks re-execution of the same transfer. The `FinalizeTransferResponse` posted back to NEAR carries `self.mint.key()` (the fake mint), not the legitimate token: [4](#0-3) 

NEAR will reject the proof because the fake token is not registered in its token registry, but the nonce is already spent on Solana. The legitimate finalization path is permanently closed.

### Impact Explanation

**Critical — Irreversible fund lock.** For every NEAR→Solana transfer:
1. The user's tokens are burned/locked on NEAR during `init_transfer`.
2. The attacker front-runs `finalize_transfer` on Solana with a fake mint, consuming the destination nonce.
3. NEAR rejects the Wormhole proof (unregistered token), so the transfer is never marked finalized.
4. The user's tokens on NEAR are permanently unclaimable. No recovery path exists because the nonce cannot be reused.

This matches the allowed impact: *"Irreversible fund lock, frozen redemption path, or permanently unclaimable user or protocol value in bridge flows."*

### Likelihood Explanation

**High.** Wormhole VAAs are public once published by the guardians. Any observer can extract a valid VAA, create a fake mint (a standard Solana operation costing fractions of a cent), and submit the front-running transaction. No privileged access, leaked keys, or colluding parties are required. The attacker only needs to be faster than the legitimate relayer, which is trivially achievable by paying a higher priority fee.

### Recommendation

Add an explicit Anchor account constraint that binds the `mint` account to the token address carried inside the verified payload. For example:

```rust
#[account(
    mut,
    mint::token_program = token_program,
    constraint = mint.key() == data.payload.token_address
        @ ErrorCode::InvalidMint,
)]
pub mint: Box<InterfaceAccount<'info, Mint>>,
```

Alternatively, derive the mint address deterministically from the payload's token identifier using a PDA (as is already done for `WRAPPED_MINT_SEED` in `deploy_token.rs`), so the caller cannot substitute an arbitrary mint. [5](#0-4) 

### Proof of Concept

1. Alice initiates a NEAR→Solana transfer of 1000 USDC. Her tokens are locked on NEAR. NEAR publishes a Wormhole VAA containing `destination_nonce = N`, `token = <USDC mint>`, `amount = 1000`, `recipient = Alice_Solana`.
2. Attacker Bob observes the VAA before any relayer submits it.
3. Bob creates a new SPL mint `FakeMint` and sets the bridge authority PDA (`seeds = [AUTHORITY_SEED]`) as its mint authority.
4. Bob calls `finalize_transfer(vaa, ...)` passing `FakeMint` as the `mint` account and `None` as the `vault` (no vault exists for `FakeMint`).
5. `UsedNonces::use_nonce(N, ...)` succeeds — nonce `N` is now permanently spent.
6. The check `mint.mint_authority.contains(authority.key)` passes for `FakeMint`.
7. The program mints 1000 `FakeMint` tokens to Alice's associated token account (worthless).
8. A `FinalizeTransferResponse` with `token = FakeMint` is posted to Wormhole.
9. NEAR receives the proof, looks up `FakeMint` in `token_address_to_id`, finds nothing, and rejects the proof.
10. The legitimate relayer attempts to submit the same VAA — `UsedNonces::use_nonce(N, ...)` returns `ErrorCode::NonceAlreadyUsed`. Alice's 1000 USDC on NEAR are permanently locked. [6](#0-5)

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer.rs (L53-57)
```rust
    #[account(
        mut,
        mint::token_program = token_program,
    )]
    pub mint: Box<InterfaceAccount<'info, Mint>>,
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer.rs (L89-136)
```rust
impl FinalizeTransfer<'_> {
    pub fn process(&mut self, data: FinalizeTransferPayload) -> Result<()> {
        UsedNonces::use_nonce(
            data.destination_nonce,
            &self.used_nonces,
            &mut self.config,
            self.authority.to_account_info(),
            self.common.payer.to_account_info(),
            &Rent::get()?,
            self.system_program.to_account_info(),
        )?;

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
        } else {
            // Bridged version. May be a fake token with our authority set but it will be ignored on the near side
            require!(
                self.mint.mint_authority.contains(self.authority.key),
                ErrorCode::InvalidBridgedToken
            );

            mint_to(
                CpiContext::new_with_signer(
                    self.token_program.to_account_info(),
                    MintTo {
                        mint: self.mint.to_account_info(),
                        to: self.token_account.to_account_info(),
                        authority: self.authority.to_account_info(),
                    },
                    &[&[AUTHORITY_SEED, &[self.config.bumps.authority]]],
                ),
                data.amount.try_into().map_err(|_| error!(ErrorCode::AmountOverflow))?,
            )?;
        }
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/finalize_transfer.rs (L138-144)
```rust
        let payload = FinalizeTransferResponse {
            token: self.mint.key(),
            amount: data.amount,
            fee_recipient: data.fee_recipient.unwrap_or_default(),
            transfer_id: data.transfer_id,
        }
        .serialize_for_near(())?;
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/deploy_token.rs (L46-53)
```rust
        init,
        payer = common.payer,
        seeds = [WRAPPED_MINT_SEED, data.payload.token.to_hashed_bytes().as_ref()],
        bump,
        mint::decimals = std::cmp::min(MAX_ALLOWED_DECIMALS, data.payload.decimals),
        mint::authority = authority,
    )]
    pub mint: Box<Account<'info, Mint>>,
```
