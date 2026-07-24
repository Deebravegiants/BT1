Let me verify the exact serialization format and check if there's any additional binding in the `finalize_transfer` payload for comparison.

The code is fully traceable. Here is the complete analysis.

---

### Title
Missing Domain Separator in `deploy_token` Signed Payload Enables Cross-Deployment Replay — (`solana/programs/bridge_token_factory/src/state/message/deploy_token.rs`)

### Summary

`DeployTokenPayload::serialize_for_near` produces a signed message body containing only `[Metadata type byte] + token + name + symbol + decimals`. No chain ID, no Solana program ID, and no nonce are included. Any two Solana bridge deployments initialized with the same `derived_near_bridge_address` (the global NEAR MPC public key) will accept each other's `deploy_token` signatures verbatim.

### Finding Description

**Signed message construction — `deploy_token`:**

`DeployTokenPayload::serialize_for_near` writes exactly:

```
[1u8 (IncomingMessageType::Metadata)] ++ borsh(token) ++ borsh(name) ++ borsh(symbol) ++ borsh(decimals)
``` [1](#0-0) 

The struct itself carries no binding fields: [2](#0-1) 

**Verification — `verify_signature`:**

The verifier hashes the serialized bytes, recovers the signer, and checks it equals `derived_near_bridge_address`. No program ID, no cluster, no nonce is checked. [3](#0-2) 

**Contrast with `finalize_transfer`:**

`FinalizeTransferPayload::serialize_for_near` explicitly writes `SOLANA_OMNI_BRIDGE_CHAIN_ID` twice (once for the token address, once for the recipient address) and includes the `destination_nonce`, the specific mint `Pubkey`, and the specific recipient `Pubkey` as additional params — providing full domain binding. [4](#0-3) 

`deploy_token` passes `AdditionalParams = ()` — nothing: [5](#0-4) 

**The only replay guard is the `init` constraint on the mint PDA:**

```rust
seeds = [WRAPPED_MINT_SEED, data.payload.token.to_hashed_bytes().as_ref()],
``` [6](#0-5) 

This PDA is derived under the *calling program's* ID. On a second deployment (different program ID), the PDA address is different, so `init` succeeds and the replay is not blocked.

**Cross-chain surface (EVM):**

The EVM `deployToken` encodes the signed message identically:

```solidity
bytes.concat(
    bytes1(uint8(BridgeTypes.PayloadType.Metadata)),  // == 1u8
    Borsh.encodeString(metadata.token),
    Borsh.encodeString(metadata.name),
    Borsh.encodeString(metadata.symbol),
    bytes1(metadata.decimals)
)
``` [7](#0-6) 

Because the NEAR MPC key (`derived_near_bridge_address` / `nearBridgeDerivedAddress`) is global, a signature produced for EVM `deployToken` is byte-for-byte valid for Solana `deploy_token` and vice versa, widening the replay surface beyond just two Solana deployments.

### Impact Explanation

An attacker who captures a valid `SignedPayload<DeployTokenPayload>` from any deployment sharing the same NEAR MPC key can submit it to a second Solana bridge instance. The second instance will:

1. Pass `verify_signature` (identical hash, same MPC key).
2. Create a new mint PDA (different program ID → different PDA address → `init` succeeds).
3. Post a `DeployTokenResponse` Wormhole message back to NEAR registering the new, unbacked mint.

This breaks canonical asset identity: two distinct Solana mints now claim to represent the same NEAR token. If NEAR processes the second Wormhole message, the registered mint address is overwritten, redirecting future `finalize_transfer` minting to the attacker-triggered mint. Even if NEAR rejects it, users on the second deployment hold tokens with no backing path.

This falls under: **High — Asset-identity divergence that breaks backing guarantees.**

### Likelihood Explanation

The precondition is two Solana bridge deployments sharing the same `derived_near_bridge_address`. This is realistic in:

- **Program upgrades**: the old and new program IDs coexist during migration; both are initialized with the same NEAR MPC key.
- **Cross-chain replay** (higher likelihood): EVM and Solana deployments already coexist in production and use the same NEAR MPC key with identical payload encoding, making this immediately exploitable without any second Solana deployment.

The attacker role is strictly unprivileged: capturing a broadcast Wormhole message or on-chain transaction is sufficient to obtain the `SignedPayload`.

### Recommendation

Add a domain separator to `DeployTokenPayload::serialize_for_near` that binds the signature to the specific deployment. At minimum, include:

1. **`SOLANA_OMNI_BRIDGE_CHAIN_ID`** — already used in `finalize_transfer`, distinguishes Solana from EVM.
2. **The program ID** (`crate::ID`) — distinguishes between different Solana program deployments.
3. **A nonce or sequence number** — prevents replay of the same token deployment across time.

The NEAR MPC signer must include these fields when constructing the payload to sign, mirroring the pattern already established in `FinalizeTransferPayload`.

### Proof of Concept

```rust
// 1. Capture a valid SignedPayload from deployment A (e.g., from a Wormhole message or tx)
let signed: SignedPayload<DeployTokenPayload> = /* captured from deployment A */;

// 2. Submit identical SignedPayload to deployment B (different program_id, same derived_near_bridge_address)
//    The only difference is the program_id used to derive PDAs.
//    verify_signature hashes only [1u8 ++ token ++ name ++ symbol ++ decimals] — identical on both.
//    The mint PDA on B is at a different address (different program_id), so `init` succeeds.

// Differential assertion:
// deployment_A.mint_pda(token) != deployment_B.mint_pda(token)  // different program IDs
// deployment_B.verify_signature(signed) == Ok(())               // same hash, same MPC key
// deployment_B.mint created                                     // unbacked wrapped token exists
```

The test is locally reproducible with two `mollusk` or `bankrun` program instances initialized with the same `derived_near_bridge_address` and different program IDs.

### Citations

**File:** solana/programs/bridge_token_factory/src/state/message/deploy_token.rs (L8-14)
```rust
#[derive(AnchorSerialize, AnchorDeserialize)]
pub struct DeployTokenPayload {
    pub token: String,
    pub name: String,
    pub symbol: String,
    pub decimals: u8,
}
```

**File:** solana/programs/bridge_token_factory/src/state/message/deploy_token.rs (L19-27)
```rust
    fn serialize_for_near(&self, _params: Self::AdditionalParams) -> Result<Vec<u8>> {
        let mut writer = BufWriter::new(Vec::with_capacity(DEFAULT_SERIALIZER_CAPACITY));
        IncomingMessageType::Metadata.serialize(&mut writer)?;
        self.serialize(&mut writer)?; // borsh encoding
        writer
            .into_inner()
            .map_err(|_| error!(ErrorCode::InvalidArgs))
    }
}
```

**File:** solana/programs/bridge_token_factory/src/state/message/mod.rs (L23-47)
```rust
impl<P: Payload> SignedPayload<P> {
    pub fn verify_signature(
        &self,
        params: P::AdditionalParams,
        derived_near_bridge_address: &[u8; 64],
    ) -> Result<()> {
        let serialized = self.payload.serialize_for_near(params)?;
        let hash = keccak::hash(&serialized);

        let signature_bytes = &self.signature[0..64];

        let signature = libsecp256k1::Signature::parse_standard_slice(signature_bytes)
            .map_err(|_| ProgramError::InvalidArgument)?;
        require!(!signature.s.is_high(), ErrorCode::MalleableSignature);

        let signer = secp256k1_recover(&hash.to_bytes(), self.signature[64], signature_bytes)
            .map_err(|_| error!(ErrorCode::SignatureVerificationFailed))?;

        require!(
            signer.0 == *derived_near_bridge_address,
            ErrorCode::SignatureVerificationFailed
        );

        Ok(())
    }
```

**File:** solana/programs/bridge_token_factory/src/state/message/finalize_transfer.rs (L20-43)
```rust
    fn serialize_for_near(&self, params: Self::AdditionalParams) -> Result<Vec<u8>> {
        let mut writer = BufWriter::new(Vec::with_capacity(DEFAULT_SERIALIZER_CAPACITY));
        // 0. prefix
        IncomingMessageType::InitTransfer.serialize(&mut writer)?;
        // 1. destination_nonce
        self.destination_nonce.serialize(&mut writer)?;
        // 2. transfer_id
        writer.write_all(&[self.transfer_id.origin_chain])?;
        self.transfer_id.origin_nonce.serialize(&mut writer)?;
        // 3. token
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.0.serialize(&mut writer)?;
        // 4. amount
        self.amount.serialize(&mut writer)?;
        // 5. recipient
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.1.serialize(&mut writer)?;
        // 6. fee_recipient
        self.fee_recipient.serialize(&mut writer)?;

        writer
            .into_inner()
            .map_err(|_| error!(ErrorCode::InvalidArgs))
    }
```

**File:** solana/programs/bridge_token_factory/src/lib.rs (L66-76)
```rust
    pub fn deploy_token(
        ctx: Context<DeployToken>,
        data: SignedPayload<DeployTokenPayload>,
    ) -> Result<()> {
        msg!("Deploying token");

        data.verify_signature((), &ctx.accounts.common.config.derived_near_bridge_address)?;
        ctx.accounts.initialize_token_metadata(data.payload)?;

        Ok(())
    }
```

**File:** solana/programs/bridge_token_factory/src/instructions/user/deploy_token.rs (L45-53)
```rust
    #[account(
        init,
        payer = common.payer,
        seeds = [WRAPPED_MINT_SEED, data.payload.token.to_hashed_bytes().as_ref()],
        bump,
        mint::decimals = std::cmp::min(MAX_ALLOWED_DECIMALS, data.payload.decimals),
        mint::authority = authority,
    )]
    pub mint: Box<Account<'info, Mint>>,
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L142-153)
```text
        bytes memory borshEncoded = bytes.concat(
            bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
            Borsh.encodeString(metadata.token),
            Borsh.encodeString(metadata.name),
            Borsh.encodeString(metadata.symbol),
            bytes1(metadata.decimals)
        );
        bytes32 hashed = keccak256(borshEncoded);

        if (ECDSA.recover(hashed, signatureData) != nearBridgeDerivedAddress) {
            revert InvalidSignature();
        }
```
