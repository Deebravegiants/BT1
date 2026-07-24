### Title
Token-2022 MetadataPointer Cross-Mint Metadata Spoofing in `log_metadata` — (`solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs`)

---

### Summary

`parse_metadata_account` for Token-2022 mints validates only that the supplied metadata account is owned by MetaplexID, but never verifies it is the canonical Metaplex PDA for the mint being registered. An attacker can point a Token-2022 mint's `MetadataPointer` at the legitimate Metaplex metadata of a *different* mint (one the attacker created with name=`USDC`, symbol=`USDC`), causing `log_metadata` to post a Wormhole message to NEAR that registers the attacker's mint under a spoofed identity.

---

### Finding Description

**Classic SPL path (safe):** Lines 116–128 compute the metadata address as the canonical Metaplex PDA for the mint:

```rust
Pubkey::find_program_address(
    &[METADATA_SEED, MetaplexID.as_ref(), &self.mint.key().to_bytes()],
    &MetaplexID,
).0
```

This is hardcoded from the mint key — an attacker cannot redirect it. [1](#0-0) 

**Token-2022 path (vulnerable):** Lines 104–106 use the address stored in the mint's `MetadataPointer` extension directly:

```rust
} else if metadata_pointer.metadata_address.0 != Pubkey::default() {
    // Third-party metadata
    self.parse_metadata_account(metadata_pointer.metadata_address.0)?
```

This address is set by whoever created the mint — the attacker. [2](#0-1) 

**`parse_metadata_account` checks (lines 72–90):**

```rust
require_keys_eq!(metadata.key(), address, ...);   // address == MetadataPointer value
if metadata.owner == &MetaplexID {
    let metadata = MplMetadata::try_deserialize(...)?;
    Ok((metadata.name.clone(), metadata.symbol.clone()))
```

The two checks are: (1) the passed account key matches the MetadataPointer value, and (2) the account is owned by MetaplexID. There is **no check** that the account is the canonical Metaplex PDA for `self.mint`. [3](#0-2) 

**Attack steps:**

1. Attacker creates ordinary SPL mint **Y** and calls the Metaplex program to create its metadata with `name="USDC"`, `symbol="USDC"`. This produces account **M** at PDA `[b"metadata", MetaplexID, Y]`, owned by MetaplexID.
2. Attacker creates Token-2022 mint **X** with a `MetadataPointer` extension whose `metadata_address` is set to **M**.
3. Attacker calls `log_metadata` passing mint **X** and account **M**.
4. `parse_metadata_account(M)`: `M.key() == M` ✓, `M.owner == MetaplexID` ✓ → deserializes → `("USDC", "USDC")`.
5. `LogMetadataPayload { token: X, name: "USDC", symbol: "USDC", decimals: X.decimals }` is posted via Wormhole to NEAR.

The mint constraint `!mint.mint_authority.contains(authority.key)` only ensures the bridge is not the mint authority; the attacker retains mint authority over **X**. [4](#0-3) 

---

### Impact Explanation

NEAR registers attacker mint **X** with name/symbol `USDC`/`USDC`. Because the attacker controls **X**'s mint authority, they can mint unlimited tokens on Solana and bridge them to NEAR as a token labeled `USDC`. Downstream integrators or users who rely on name/symbol for token identification (rather than the on-chain address) may treat the attacker's token as the real USDC, enabling asset-identity spoofing and potential financial loss. This falls under **"Asset-identity, token-mapping divergence that breaks backing guarantees."**

---

### Likelihood Explanation

The attack requires no privileged access: creating SPL mints, creating Metaplex metadata, and creating Token-2022 mints with custom extensions are all permissionless Solana operations. The call to `log_metadata` is also permissionless. The only cost is rent for the accounts involved.

---

### Recommendation

For the Token-2022 third-party metadata branch, verify that the MetadataPointer address equals the canonical Metaplex PDA for the mint before accepting it:

```rust
} else if metadata_pointer.metadata_address.0 != Pubkey::default() {
    let expected = Pubkey::find_program_address(
        &[METADATA_SEED, MetaplexID.as_ref(), &self.mint.key().to_bytes()],
        &MetaplexID,
    ).0;
    require_keys_eq!(
        metadata_pointer.metadata_address.0,
        expected,
        ErrorCode::InvalidTokenMetadataAddress,
    );
    self.parse_metadata_account(expected)?
```

This mirrors the safe check already used for classic SPL tokens. [1](#0-0) 

---

### Proof of Concept

```rust
// 1. Create SPL mint Y and Metaplex metadata with name="USDC", symbol="USDC"
//    → produces account M at PDA [b"metadata", MetaplexID, Y], owner=MetaplexID

// 2. Create Token-2022 mint X with MetadataPointer pointing to M
let mint_x = create_token_2022_mint_with_metadata_pointer(M);

// 3. Call log_metadata with mint=X, metadata=M
log_metadata(mint_x, Some(M));

// 4. parse_metadata_account(M):
//    - M.key() == M  ✓
//    - M.owner == MetaplexID  ✓
//    - deserialize → name="USDC", symbol="USDC"

// 5. Wormhole message posted:
//    LogMetadataPayload { token: X, name: "USDC", symbol: "USDC", decimals: ... }
// Assert: NEAR registers X as "USDC"/"USDC" — spoofed identity confirmed.
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

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L104-106)
```rust
                } else if metadata_pointer.metadata_address.0 != Pubkey::default() {
                    // Third-party metadata
                    self.parse_metadata_account(metadata_pointer.metadata_address.0)?
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/log_metadata.rs (L116-128)
```rust
            // Only metaplex is supported for the classic SPL tokens
            self.parse_metadata_account(
                Pubkey::find_program_address(
                    &[
                        METADATA_SEED,
                        MetaplexID.as_ref(),
                        &self.mint.key().to_bytes(),
                    ],
                    &MetaplexID,
                )
                .0,
            )?
        };
```
