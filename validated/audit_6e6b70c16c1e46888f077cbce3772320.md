### Title
Token-2022 Transfer-Fee Extension Causes Vault Underfunding in Solana `init_transfer` — (`solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs`)

---

### Summary

The Solana bridge's `init_transfer` uses `transfer_checked` (Token-2022 compatible) to lock native tokens into the vault, then posts a Wormhole message encoding `payload.amount` — the caller-supplied amount. For Token-2022 mints that carry the **transfer-fee extension**, `transfer_checked` silently withholds a fee from the recipient, so the vault receives `amount − fee` while the Wormhole message (and therefore the NEAR side) records the full `amount`. Every such transfer creates an unbacked shortfall in the vault, and the discrepancy accumulates until the vault cannot satisfy redemptions.

---

### Finding Description

`InitTransfer::process` in `init_transfer.rs` follows this sequence for native (non-bridged) tokens:

1. Validate `payload.amount > payload.fee`.
2. Call `transfer_checked(…, payload.amount, self.mint.decimals)` — moves tokens from the user's account to the vault PDA.
3. Call `self.common.post_message(payload.serialize_for_near(…))` — serialises `self.amount` (i.e. `payload.amount`) into the Wormhole VAA. [1](#0-0) 

The Wormhole payload is built by `InitTransferPayload::serialize_for_near`, which writes `self.amount` verbatim: [2](#0-1) 

The NEAR bridge reads the VAA and releases exactly that amount to the recipient: [3](#0-2) 

**Token-2022 transfer-fee mechanics**: When a mint has the `TransferFeeConfig` extension, `transfer_checked` succeeds but the recipient receives `amount − fee`; the fee is withheld inside the recipient's token account. No extra accounts are required — the fee is applied automatically by the Token-2022 program. This is distinct from transfer hooks (which require extra accounts and cause a runtime failure, as documented in `solana/SECURITY.md`). [4](#0-3) 

The Solana SECURITY.md documents transfer-hook tokens as unsupported (they fail at runtime), but says **nothing** about transfer-fee tokens. The EVM SECURITY.md explicitly marks fee-on-transfer tokens as unsupported, but that note does not extend to the Solana program. [5](#0-4) 

Because `log_metadata` is permissionless, any Token-2022 mint — including one with a transfer-fee extension — can be registered, causing a vault to be created and the native-token path in `init_transfer` to be exercised.

---

### Impact Explanation

Each `init_transfer` call with a transfer-fee Token-2022 mint deposits `amount − fee` into the vault but instructs NEAR to release `amount`. The vault's backing is permanently short by `fee` per transfer. When users later bridge back (NEAR → Solana `finalize_transfer`), the vault will eventually lack sufficient balance to honour redemptions, causing irreversible fund lock for later redeemers. This is a **backing-guarantee violation** matching the allowed High impact category: *"balance-accounting divergence that breaks backing guarantees."*

---

### Likelihood Explanation

`log_metadata` is explicitly permissionless. [6](#0-5) 

An unprivileged attacker can deploy a Token-2022 mint with a transfer-fee extension, call `log_metadata` to register it, wait for NEAR-side metadata processing, and then call `init_transfer` repeatedly. No privileged role, leaked key, or external dependency compromise is required. The attacker's only cost is the transfer fee on their own tokens; the vault shortfall is borne by future redeemers.

---

### Recommendation

After `transfer_checked` completes, read the vault's post-transfer balance and use the **actual received amount** (vault balance delta) as the value serialised into the Wormhole message, rather than `payload.amount`. Alternatively, explicitly reject Token-2022 mints that carry the `TransferFeeConfig` extension during `log_metadata` registration (analogous to how the EVM bridge documents fee-on-transfer tokens as unsupported), and enforce the same check at `init_transfer` time.

---

### Proof of Concept

1. Attacker deploys a Token-2022 mint `FOT` with `TransferFeeConfig` set to 1 % (100 bps).
2. Attacker calls `log_metadata` for `FOT` — permissionless, vault PDA is created.
3. NEAR side processes the metadata; a wrapped `FOT` token is deployed on NEAR.
4. Attacker calls `init_transfer` with `payload.amount = 10_000`, `payload.fee = 0`.
   - `transfer_checked(10_000, decimals)` executes; vault receives **9_900** (100 withheld as transfer fee).
   - `serialize_for_near` encodes `amount = 10_000` into the Wormhole VAA.
5. NEAR bridge reads the VAA and mints/releases **10_000** wrapped `FOT` to the recipient.
6. Vault holds 9_900; NEAR supply is 10_000 — **100-token shortfall per transfer**.
7. Repeated calls drain the vault; the last redeemers cannot withdraw their tokens. [7](#0-6) [8](#0-7)

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/user/init_transfer.rs (L88-127)
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
        } else {
            // Bridged version. May be a fake token with our authority set but it will be ignored on the near side
            require!(
                self.mint.mint_authority.contains(self.authority.key),
                ErrorCode::InvalidBridgedToken
            );

            burn(
                CpiContext::new(
                    self.token_program.to_account_info(),
                    Burn {
                        mint: self.mint.to_account_info(),
                        from: self.from.to_account_info(),
                        authority: self.user.to_account_info(),
                    },
                ),
                payload.amount.try_into().map_err(|_| error!(ErrorCode::InvalidArgs))?,
            )?;
        }

        self.common.post_message(payload.serialize_for_near((
            self.common.sequence.sequence,
            self.user.key(),
            self.mint.key(),
        ))?)?;
```

**File:** solana/programs/bridge_token_factory/src/state/message/init_transfer.rs (L19-45)
```rust
    fn serialize_for_near(&self, params: Self::AdditionalParams) -> Result<Vec<u8>> {
        let mut writer = BufWriter::new(Vec::with_capacity(DEFAULT_SERIALIZER_CAPACITY));
        // 0. OutgoingMessageType::InitTransfer
        OutgoingMessageType::InitTransfer.serialize(&mut writer)?;
        // 1. sender
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.1.serialize(&mut writer)?;
        // 2. token
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.2.serialize(&mut writer)?;
        // 3. nonce
        params.0.serialize(&mut writer)?;
        // 4. amount
        self.amount.serialize(&mut writer)?;
        // 5. fee
        self.fee.serialize(&mut writer)?;
        // 6. native_fee
        u128::from(self.native_fee).serialize(&mut writer)?;
        // 7. recipient
        self.recipient.serialize(&mut writer)?;
        // 8. message
        self.message.serialize(&mut writer)?;

        writer
            .into_inner()
            .map_err(|_| error!(ErrorCode::InvalidArgs))
    }
```

**File:** near/omni-bridge/src/lib.rs (L726-736)
```rust
        let transfer_message = TransferMessage {
            origin_nonce: init_transfer.origin_nonce,
            token: init_transfer.token,
            amount: Self::denormalize_amount(init_transfer.amount.0, decimals).into(),
            recipient: init_transfer.recipient,
            fee: Self::denormalize_fee(&init_transfer.fee, decimals),
            sender: init_transfer.sender,
            msg: init_transfer.msg,
            destination_nonce,
            origin_transfer_id: None,
        };
```

**File:** solana/SECURITY.md (L19-19)
```markdown
- **Token-2022 tokens with transfer hooks are not supported** — Transfer hook extra account metas are not included in instruction account sets. Affected tokens will fail at runtime (denial, not fund loss).
```

**File:** evm/SECURITY.md (L7-7)
```markdown
- **Fee-on-transfer tokens not supported**: `initTransfer` emits the requested `amount`, not the actual received balance. Fee-on-transfer and rebasing tokens are intentionally unsupported
```

**File:** evm/SECURITY.md (L8-8)
```markdown
- **`logMetadata` and `deployToken` are permissionless**: Anyone can call `logMetadata` for any ERC20, and anyone can submit a valid MPC signature to `deployToken`. This is by design — the bridge is fully permissionless
```
