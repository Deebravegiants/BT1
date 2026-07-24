The code is fully readable. Let me trace the exact execution path for the proposed attack.

### Title
Token-2022 MetadataPointer Cross-Mint Metadata Spoofing in `log_metadata` — (`solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs`)

---

### Summary

`LogMetadata::process` reads name/symbol from a third-party metadata account identified only by the address stored in the mint's `MetadataPointer` extension. It verifies the passed account's **key** matches the pointer and that the account is **owned by MetaplexID**, but it never verifies that the deserialized metadata's `mint` field matches the mint being logged. An unprivileged attacker can point a Token-2022 mint's `MetadataPointer` at a legitimate Metaplex metadata account belonging to a *different* mint, causing the bridge to emit a `LogMetadataPayload` that attributes the victim token's name/symbol to the attacker's mint pubkey.

---

### Finding Description

In `process()`, the Token-2022 branch reads the `MetadataPointer` extension and, when the pointer address is neither the mint itself nor `Pubkey::default()`, delegates to `parse_metadata_account`: [1](#0-0) 

`parse_metadata_account` performs two checks before accepting the account:

1. The passed account's **key** equals the pointer address.
2. The account's **owner** is `MetaplexID`. [2](#0-1) 

Neither check binds the deserialized metadata to the mint being logged. The `MplMetadata` struct contains a `mint` field that identifies which mint the metadata belongs to, but it is never compared against `self.mint.key()`. The payload is then constructed with `token: self.mint.key()` (the attacker's mint) but `name`/`symbol` from the foreign metadata account: [3](#0-2) 

---

### Impact Explanation

The `LogMetadataPayload` is posted as a Wormhole message consumed by NEAR to register the token's identity. A spoofed payload registers `mint_B` on NEAR under `mint_A`'s name and symbol (e.g., "USD Coin" / "USDC"). This is a direct asset-identity divergence: the on-chain token identity recorded in the bridge's cross-chain registry does not correspond to the actual token, enabling impersonation of any token whose Metaplex metadata exists on-chain.

---

### Likelihood Explanation

The attack requires no privileged access. Creating a Token-2022 mint with an arbitrary `MetadataPointer` is a standard, permissionless operation. Metaplex metadata accounts for popular tokens (USDC, USDT, etc.) already exist on mainnet. The entire exploit is executable in a single transaction by any wallet.

---

### Recommendation

After deserializing the `MplMetadata` account, assert that its `mint` field matches the mint being logged:

```rust
let metadata_account = MplMetadata::try_deserialize(&mut data.as_ref())?;
require_keys_eq!(
    metadata_account.mint,
    self.mint.key(),
    ErrorCode::InvalidTokenMetadataAddress,
);
Ok((metadata_account.name.clone(), metadata_account.symbol.clone()))
```

This closes the gap by binding the metadata content to the specific mint, regardless of what address the `MetadataPointer` extension contains.

---

### Proof of Concept

```
1. Create mint_A (any SPL/Token-2022 mint).
2. Call Metaplex `create_metadata_accounts_v3` for mint_A with
   name="USD Coin", symbol="USDC".
   → metadata_A_PDA = find_program_address(
       [b"metadata", MetaplexID, mint_A], MetaplexID)
   → owned by MetaplexID, mint field = mint_A.

3. Create mint_B as a Token-2022 mint with:
   - MetadataPointer extension pointing to metadata_A_PDA.
   - mint_authority ≠ bridge authority (passes the constraint).

4. Call log_metadata(mint = mint_B, metadata = metadata_A_PDA).

5. Inside parse_metadata_account(metadata_A_PDA):
   - require_keys_eq!(metadata_A_PDA, metadata_A_PDA) → PASS
   - metadata.owner == MetaplexID → PASS
   - MplMetadata::try_deserialize → succeeds, returns ("USD Coin","USDC")

6. Wormhole message emitted:
   LogMetadataPayload {
     token:   mint_B,       ← attacker's mint
     name:    "USD Coin",   ← stolen from mint_A
     symbol:  "USDC",       ← stolen from mint_A
     decimals: mint_B.decimals,
   }

7. NEAR registers mint_B as "USDC", breaking the token-identity invariant.
```

### Citations

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
