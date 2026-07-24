### Title
Token-2022 Metadata Pointer Cross-Mint Identity Hijacking in `log_metadata` — (`solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs`)

---

### Summary

`parse_metadata_account` verifies that the supplied `metadata` account key matches the address stored in mint A's `MetadataPointer` extension, but never checks that the deserialized Metaplex metadata's own `mint` field equals `self.mint.key()`. An unprivileged attacker can create a Token-2022 mint A whose `metadata_pointer` points to the Metaplex PDA of any legitimate token B, then call `log_metadata` to emit a Wormhole VAA that binds mint A's on-chain address to token B's name and symbol.

---

### Finding Description

The Token-2022 "third-party metadata" branch in `process()` reads the `metadata_pointer` extension from mint A and delegates to `parse_metadata_account` with whatever address the pointer contains: [1](#0-0) 

`parse_metadata_account` performs two checks: the passed account key must equal the pointer address, and the account must be owned by `MetaplexID`. It then deserializes and returns `name`/`symbol` directly: [2](#0-1) 

There is no check that `metadata.mint == self.mint.key()`. The Metaplex `MetadataAccount` struct carries a `mint` field that records which mint the metadata was created for, but it is never read here.

The payload is then assembled with `token = self.mint.key()` (mint A) but `name`/`symbol` from the foreign metadata (token B): [3](#0-2) 

The `mint` account constraint only requires that the bridge authority is **not** the mint authority — it does not restrict who created the mint or what its `metadata_pointer` contains: [4](#0-3) 

---

### Impact Explanation

The spoofed VAA is consumed on NEAR via `deploy_token_callback`, which trusts the `LogMetadataMessage` fields verbatim: [5](#0-4) 

NEAR registers `Sol:mint_A` as a bridgeable token with token B's `name` and `symbol`. Any user who subsequently bridges tokens through the NEAR-side wrapped token for `Sol:mint_A` will see it presented as token B. This constitutes asset-identity divergence: the on-chain token address and the displayed identity are decoupled, breaking the backing guarantee that every `LogMetadata` Wormhole message must bind name/symbol to the exact mint whose pubkey appears in the payload.

The `LogMetadataWh` struct on the NEAR prover side passes `name` and `symbol` through without any cross-validation: [6](#0-5) 

---

### Likelihood Explanation

All preconditions are trivially achievable by any unprivileged actor:

1. Create a Token-2022 mint with any keypair as mint authority (not the bridge authority PDA).
2. During mint initialization, set the `MetadataPointer` extension to the Metaplex PDA of any established token B — this is a standard Token-2022 feature requiring no special permission.
3. Token B's Metaplex metadata PDA already exists on-chain for any real token.
4. Call `log_metadata` with mint A and token B's metadata account. No signature, no privileged role, no fee beyond Solana transaction costs.

---

### Recommendation

After deserializing the Metaplex metadata in `parse_metadata_account`, add a binding check:

```rust
if metadata.owner == &MetaplexID {
    let data = metadata.try_borrow_data()?;
    let metadata = MplMetadata::try_deserialize(&mut data.as_ref())?;
    // ADD THIS CHECK:
    require_keys_eq!(
        metadata.mint,
        self.mint.key(),
        ErrorCode::InvalidTokenMetadataAddress,
    );
    Ok((metadata.name.clone(), metadata.symbol.clone()))
}
```

This ensures the Metaplex metadata account was created for the exact mint being registered, closing the cross-mint identity substitution path.

---

### Proof of Concept

1. Attacker generates keypair `mint_A`.
2. Creates a Token-2022 mint at `mint_A` with `mint_authority = attacker_keypair` and a `MetadataPointer` extension set to `find_program_address(["metadata", MetaplexID, mint_B], MetaplexID)` — the Metaplex PDA of a high-value token B (e.g., USDC).
3. Calls `log_metadata` with accounts: `mint = mint_A`, `metadata = metaplex_PDA_of_mint_B`, `token_program = Token-2022`.
4. Inside `process()`: the `MetadataPointer` address ≠ `mint_A.key()` and ≠ `Pubkey::default()`, so `parse_metadata_account(metaplex_PDA_of_mint_B)` is called.
5. `parse_metadata_account` passes both checks (key match, owner = MetaplexID), deserializes token B's metadata, returns `("USD Coin", "USDC")`.
6. Emitted `LogMetadataPayload`: `token = Sol:mint_A`, `name = "USD Coin"`, `symbol = "USDC"`, `decimals = mint_A.decimals`.
7. Wormhole VAA is posted. Relayer submits it to NEAR `deploy_token`.
8. NEAR's `deploy_token_callback` calls `deploy_token_internal` registering `Sol:mint_A` with name "USD Coin" and symbol "USDC".
9. Differential assertion: NEAR token registry maps `Sol:mint_A → {name: "USD Coin", symbol: "USDC"}` while the real USDC mint address is `Sol:mint_B` — the two are distinct, confirming identity hijacking.

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L41-45)
```rust
    #[account(
        constraint = !mint.mint_authority.contains(authority.key),
        mint::token_program = token_program,
    )]
    pub mint: Box<InterfaceAccount<'info, Mint>>,
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L78-86)
```rust
        require_keys_eq!(
            metadata.key(),
            address,
            ErrorCode::InvalidTokenMetadataAddress,
        );
        if metadata.owner == &MetaplexID {
            let data = metadata.try_borrow_data()?;
            let metadata = MplMetadata::try_deserialize(&mut data.as_ref())?;
            Ok((metadata.name.clone(), metadata.symbol.clone()))
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L98-106)
```rust
            if let Ok(metadata_pointer) = mint_with_extension.get_extension::<MetadataPointer>() {
                if metadata_pointer.metadata_address.0 == self.mint.key() {
                    // Embedded metadata
                    let metadata =
                        mint_with_extension.get_variable_len_extension::<TokenMetadata>()?;
                    (metadata.name, metadata.symbol)
                } else if metadata_pointer.metadata_address.0 != Pubkey::default() {
                    // Third-party metadata
                    self.parse_metadata_account(metadata_pointer.metadata_address.0)?
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L130-136)
```rust
        let payload = LogMetadataPayload {
            token: self.mint.key(),
            name: name.trim_end_matches('\0').to_string(),
            symbol: symbol.trim_end_matches('\0').to_string(),
            decimals: self.mint.decimals,
        }
        .serialize_for_near(())?;
```

**File:** near/omni-bridge/src/lib.rs (L1159-1178)
```rust
        let Ok(ProverResult::LogMetadata(metadata)) = call_result else {
            env::panic_str(BridgeError::InvalidProofMessage.to_string().as_str());
        };

        let chain = metadata.emitter_address.get_chain();
        require!(
            self.factories.get(&chain) == Some(metadata.emitter_address),
            BridgeError::UnknownFactory.as_ref()
        );

        self.deploy_token_internal(
            chain,
            &metadata.token_address,
            BasicMetadata {
                name: metadata.name,
                symbol: metadata.symbol,
                decimals: metadata.decimals,
            },
            attached_deposit,
        )
```

**File:** near/omni-prover/wormhole-omni-prover-proxy/src/parsed_vaa.rs (L125-132)
```rust
#[derive(Debug, BorshDeserialize)]
struct LogMetadataWh {
    payload_type: ProofKind,
    token_address: OmniAddress,
    name: String,
    symbol: String,
    decimals: u8,
}
```
