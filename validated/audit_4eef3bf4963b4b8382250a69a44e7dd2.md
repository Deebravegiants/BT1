The exploit is valid. Let me trace through the exact code path to confirm.

**Trace through `process()` for mint_B (Token-2022 with MetadataPointer → mint_A's Metaplex PDA):**

1. `token_program.key() == token_2022::ID` → enters Token-2022 branch [1](#0-0) 

2. Reads `MetadataPointer` from mint_B → `metadata_pointer.metadata_address.0` = mint_A's Metaplex PDA (not mint_B's key, not default) → enters "Third-party metadata" branch [2](#0-1) 

3. Calls `parse_metadata_account(mint_A_metadata_PDA)` [3](#0-2) 

**Inside `parse_metadata_account`:**

- `require_keys_eq!(metadata.key(), address, ...)` — attacker passes mint_A's metadata account, and `address` is mint_A's metadata PDA (from the pointer), so this **passes**. [4](#0-3) 
- `metadata.owner == &MetaplexID` — mint_A's metadata account is genuinely owned by Metaplex, so this **passes**. [5](#0-4) 
- Returns `(mint_A.name, mint_A.symbol)` — **no check that `MplMetadata.mint == self.mint.key()`**. [6](#0-5) 

4. `LogMetadataPayload { token: self.mint.key(), ... }` — `token` is **mint_B's pubkey**, but `name`/`symbol` are mint_A's. [7](#0-6) 

---

### Title
Metadata spoofing via Token-2022 MetadataPointer cross-mint redirect — (`solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs`)

### Summary
`LogMetadata::process` reads name/symbol from whichever account the mint's `MetadataPointer` extension points to, but never verifies that the deserialized `MplMetadata.mint` field matches the mint being logged. An attacker can point mint_B's `MetadataPointer` at mint_A's legitimate Metaplex metadata PDA, causing the bridge to emit a Wormhole VAA that attributes mint_A's name/symbol to mint_B's pubkey.

### Finding Description
In `parse_metadata_account`, the only binding checks are:

1. The passed account key equals the pointer address (line 78–82) — satisfied because the attacker controls the pointer.
2. The account is owned by `MetaplexID` (line 83) — satisfied because Metaplex genuinely created it for mint_A.

The missing check is `metadata.mint == self.mint.key()`. Every Metaplex `MetadataAccount` stores the mint it was created for in its `mint` field, but this field is never read or validated here. [5](#0-4) 

### Impact Explanation
The `LogMetadataPayload` is the cross-chain signal that registers a Solana token on NEAR with a given name, symbol, and decimals. [8](#0-7) 

By spoofing name/symbol, an attacker registers a worthless mint_B on NEAR under the identity of a valuable token (e.g., "USD Coin" / "USDC"). Users who see the NEAR-side token registration may bridge funds into mint_B believing it is the legitimate asset, receiving unbacked tokens. This is a concrete asset-identity divergence that breaks the backing guarantee.

### Likelihood Explanation
Fully unprivileged. Creating a Token-2022 mint with an arbitrary `MetadataPointer` requires no special permissions — any wallet can do it. Creating a Metaplex metadata account for mint_A is also permissionless. The attack requires two standard on-chain transactions before calling `log_metadata`.

### Recommendation
After deserializing the `MplMetadata` account, assert that its `mint` field matches the mint being logged:

```rust
// In parse_metadata_account, after try_deserialize:
let metadata = MplMetadata::try_deserialize(&mut data.as_ref())?;
require_keys_eq!(
    metadata.mint,
    self.mint.key(),
    ErrorCode::InvalidTokenMetadataAddress,
);
Ok((metadata.name.clone(), metadata.symbol.clone()))
``` [9](#0-8) 

### Proof of Concept
1. Create `mint_A` (any SPL token).
2. Call Metaplex `create_metadata_accounts_v3` for `mint_A` with `name="USD Coin"`, `symbol="USDC"`. This produces a PDA at `[b"metadata", MetaplexID, mint_A]` owned by `MetaplexID`.
3. Create `mint_B` as a Token-2022 mint with a `MetadataPointer` extension whose `metadata_address` is set to `mint_A`'s Metaplex PDA.
4. Call `log_metadata` for `mint_B`, passing `mint_A`'s Metaplex PDA as the `metadata` `UncheckedAccount`.
5. Observe: `require_keys_eq` passes (pointer == passed account), owner check passes (MetaplexID), deserialization succeeds, and the emitted VAA contains `token=mint_B`, `name="USD Coin"`, `symbol="USDC"`.
6. On NEAR, `mint_B` is now registered as "USD Coin / USDC", enabling user confusion and potential fund loss.

### Citations

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L72-90)
```rust
    fn parse_metadata_account(&self, address: Pubkey) -> Result<(String, String)> {
        let metadata = self
            .metadata
            .as_ref()
            .ok_or_else(|| error!(ErrorCode::TokenMetadataNotProvided))?
            .to_account_info();
        require_keys_eq!(
            metadata.key(),
            address,
            ErrorCode::InvalidTokenMetadataAddress,
        );
        if metadata.owner == &MetaplexID {
            let data = metadata.try_borrow_data()?;
            let metadata = MplMetadata::try_deserialize(&mut data.as_ref())?;
            Ok((metadata.name.clone(), metadata.symbol.clone()))
        } else {
            Ok((String::default(), String::default()))
        }
    }
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L92-92)
```rust
        let (name, symbol) = if self.token_program.key() == token_2022::ID {
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L104-106)
```rust
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

**File:** solana/programs/bridge_token_factory/src/state/message/log_metadata.rs (L8-13)
```rust
pub struct LogMetadataPayload {
    pub token: Pubkey,
    pub name: String,
    pub symbol: String,
    pub decimals: u8,
}
```
