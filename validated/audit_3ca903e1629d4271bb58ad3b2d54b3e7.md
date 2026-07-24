The critical code path is now clear. Let me confirm the exact mechanics of the `log_metadata` vault creation and the `transfer_checked` call.

The vulnerability is **real and valid**. Here is the complete analysis:

---

### Title
Token-2022 Transfer Fee Causes Vault Under-Crediting vs. Wormhole Message Over-Reporting — (`solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs`)

---

### Summary

`InitTransfer::process` calls `transfer_checked` with the raw `payload.amount`, but for Token-2022 mints with a `TransferFeeConfig` extension, the SPL Token-2022 runtime withholds a fee from the recipient (the vault). The vault receives `amount - fee`, yet the Wormhole message serializes and broadcasts the full `payload.amount`. NEAR credits the full amount, creating unbacked supply.

---

### Finding Description

**Step 1 — Permissionless vault creation via `log_metadata`**

`LogMetadata::process` uses `init_if_needed` on the vault PDA and has no restriction on Token-2022 extensions: [1](#0-0) 

The only constraint on the mint is that the bridge authority is **not** the mint authority (i.e., it is a native Solana token, not a bridged one): [2](#0-1) 

Any unprivileged user can call `log_metadata` with a Token-2022 mint that has `TransferFeeConfig` enabled, which atomically creates the vault PDA and emits a Wormhole registration message to NEAR.

**Step 2 — `transfer_checked` silently withholds the fee from the vault**

In `InitTransfer::process`, the transfer to the vault uses the raw `payload.amount`: [3](#0-2) 

Under Token-2022's `TransferFeeConfig`, `transfer_checked(amount)` debits `amount` from the sender but credits only `amount - fee` to the vault (the fee is withheld in the vault account's `withheld_amount` field, inaccessible to the bridge).

**Step 3 — Wormhole message reports the full `payload.amount`**

Immediately after the transfer, the message is posted with the same unmodified `payload.amount`: [4](#0-3) 

Which serializes `self.amount` (the full amount) into the cross-chain payload: [5](#0-4) 

**Invariant broken:** vault holds `amount - fee`, NEAR is told `amount`.

---

### Impact Explanation

- NEAR credits the full `amount` to the recipient.
- The vault is short by `fee` per transfer.
- Cumulative shortfall grows with every `init_transfer` on a fee-bearing mint.
- When users attempt to redeem on NEAR and `finalize_transfer` is called on Solana, the vault eventually cannot satisfy all outstanding claims — the last redeemers receive nothing, permanently locking their NEAR-side tokens.
- This is a **balance-accounting divergence** producing **unbacked supply on NEAR** and **irreversible fund lock** for later redeemers.

---

### Likelihood Explanation

- Token-2022 transfer fees are a standard, widely-used extension (e.g., USDC on Token-2022 uses it).
- `log_metadata` is fully permissionless — no admin approval is required to register a fee-bearing mint and create its vault.
- The attacker needs no special privileges: deploy a Token-2022 mint with fees, call `log_metadata`, call `init_transfer`. All public instructions.
- The bug also affects any legitimate Token-2022 token with fees that gets registered by honest users.

---

### Recommendation

After `transfer_checked`, read the vault's actual post-transfer balance (or compute `amount - withheld_fee` using `calculate_fee` from the `TransferFeeConfig` extension) and use **that net amount** in the Wormhole message instead of `payload.amount`. Alternatively, reject mints that have `TransferFeeConfig` enabled in `log_metadata` and `init_transfer` by inspecting the mint's extensions before proceeding.

---

### Proof of Concept

```
1. Deploy Token-2022 mint M with TransferFeeConfig: 1% fee, max_fee = u64::MAX
2. Mint 10_000 tokens of M to attacker wallet W
3. Call log_metadata(mint=M) → vault PDA V is created; NEAR registers M
4. Call init_transfer(mint=M, amount=1000, recipient="attacker.near", fee=0, native_fee=0)
   - transfer_checked(1000) executes:
       W debited 1000
       V credited 990  (10 withheld as TransferFee)
   - Wormhole message emitted: amount=1000
5. NEAR processes message → credits attacker.near with 1000 M tokens
6. Attacker redeems 1000 M on NEAR → finalize_transfer on Solana tries to send 1000 from V
   - V only has 990 → transaction fails (or if other deposits exist, drains them)
7. Net result: 10 tokens of unbacked supply on NEAR per iteration; vault is insolvent after enough iterations
```

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L41-45)
```rust
    #[account(
        constraint = !mint.mint_authority.contains(authority.key),
        mint::token_program = token_program,
    )]
    pub mint: Box<InterfaceAccount<'info, Mint>>,
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L50-62)
```rust
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

**File:** solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs (L90-102)
```rust
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

**File:** solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs (L123-127)
```rust
        self.common.post_message(payload.serialize_for_near((
            self.common.sequence.sequence,
            self.user.key(),
            self.mint.key(),
        ))?)?;
```

**File:** solana/programs/bridge_token_factory/src/state/message/init_transfer.rs (L31-33)
```rust
        // 4. amount
        self.amount.serialize(&mut writer)?;
        // 5. fee
```
