### Title
Cross-Chain Replay of `deployToken` MPC Signature Due to Missing Chain ID Binding — (`near/omni-bridge/src/lib.rs`, `evm/src/omni-bridge/contracts/OmniBridge.sol`, `starknet/src/bridge_types.cairo`, `solana/programs/bridge_token_factory/src/state/message/deploy_token.rs`, `aptos/sources/omni_bridge.move`)

---

### Summary

The `MetadataPayload` signed by the NEAR MPC signer for `deployToken` / `deploy_token` does not include a destination chain ID. Because the same MPC key and derived address (`nearBridgeDerivedAddress`) is shared across all destination chains, a valid `deployToken` signature produced for one chain is cryptographically valid on every other chain. An unprivileged attacker can observe the signature on-chain and replay it to any other chain, deploying a bridge token without NEAR's knowledge and permanently blocking the legitimate deployment path for that token on the target chain.

---

### Finding Description

The NEAR bridge constructs and signs a `MetadataPayload` in `log_metadata_callback`:

```rust
// near/omni-bridge/src/lib.rs  lines 345–354
let metadata_payload = MetadataPayload {
    prefix: PayloadType::Metadata,
    token: token_id.to_string(),
    name: metadata.name,
    symbol: metadata.symbol,
    decimals: metadata.decimals,
};
let payload = near_sdk::env::keccak256_array(
    borsh::to_vec(&metadata_payload).near_expect(BridgeError::Borsh),
);
```

The payload contains only `[prefix, token, name, symbol, decimals]` — **no destination chain ID**.

Every destination chain verifies this signature against the same `nearBridgeDerivedAddress` and reconstructs the same chain-ID-free payload:

- **EVM** (`OmniBridge.sol` lines 142–148): `[PayloadType::Metadata, token, name, symbol, decimals]`
- **StarkNet** (`bridge_types.cairo` lines 36–44, `MetadataPayloadTrait::to_borsh`): `[PayloadType::Metadata, token, name, symbol, decimals]`
- **Solana** (`deploy_token.rs` lines 19–26): `[IncomingMessageType::Metadata, token, name, symbol, decimals]`
- **Aptos** (`omni_bridge.move` lines 370–372): `metadata_to_borsh()` — same structure

This is in direct contrast to `finTransfer`, where every chain correctly binds the payload to the destination chain:

- **EVM** (`OmniBridge.sol` line 294): `bytes1(omniBridgeChainId)` is embedded in the signed bytes
- **Aptos** (`omni_bridge.move` line 450): `transfer_message_to_borsh(state.chain_id)`
- **StarkNet** (`bridge_types.cairo` line 61): `to_borsh(self: @TransferMessagePayload, chain_id: u8)`

The `deployToken` path has no equivalent chain binding.

---

### Impact Explanation

An attacker who observes a valid `deployToken` calldata on chain A (e.g., EVM Ethereum) can extract the `(signatureData, MetadataPayload)` tuple and submit it verbatim to any other chain B (e.g., EVM Arbitrum, Base, BNB, StarkNet, Solana, Aptos). The signature passes verification on chain B because the signed digest is identical.

Consequences on chain B:
1. The bridge token is deployed and registered in the chain B bridge's token mapping (`nearToEthToken`, `near_to_starknet_token`, etc.) without NEAR ever recording this deployment.
2. NEAR has no record of the token on chain B, so it will never sign a `finTransfer` for that token on chain B — the deployed token is permanently inert.
3. When the protocol later legitimately attempts to deploy the same token on chain B, the call reverts with `ERR_TOKEN_EXIST` (EVM), `ERR_TOKEN_ALREADY_DEPLOYED` (StarkNet/Aptos), or equivalent — **permanently blocking the legitimate deployment path**.

This satisfies two allowed impact categories:
- **High**: Acceptance of insufficiently-bound signatures that bypass execution gates.
- **Critical** (if the token is a high-value asset): Irreversible frozen redemption path — the token can never be properly bridged to chain B.

---

### Likelihood Explanation

- The `deployToken` signature is submitted as public calldata on the originating chain and is trivially extractable by any observer.
- No privileged access, leaked key, or colluding party is required.
- The attacker only needs to call `deployToken` / `deploy_token` on the target chain with the copied arguments.
- The Omni Bridge is deployed on multiple EVM chains (Eth, Arb, Base, BNB, Pol, HyperEvm) plus Solana, StarkNet, and Aptos — all sharing the same MPC key — making the replay surface wide.

Likelihood: **High**.

---

### Recommendation

Include the destination chain ID in the `MetadataPayload` before it is hashed and signed, mirroring the existing pattern used by `TransferMessagePayload`:

```rust
// near/omni-bridge/src/lib.rs — log_metadata_callback
let metadata_payload = MetadataPayload {
    prefix: PayloadType::Metadata,
    destination_chain: destination_chain_id,  // add this field
    token: token_id.to_string(),
    name: metadata.name,
    symbol: metadata.symbol,
    decimals: metadata.decimals,
};
```

Each destination chain must then include its own `omniBridgeChainId` when reconstructing the payload for signature verification, exactly as `finTransfer` already does. The NEAR side must be updated to sign one payload per destination chain rather than a single chain-agnostic payload.

---

### Proof of Concept

1. Call `log_metadata("token.near")` on NEAR. NEAR MPC signs `keccak256(borsh([0x01, "token.near", "Token", "TKN", 18]))` and emits the signature.
2. The relayer submits `deployToken(sig, {token:"token.near", name:"Token", symbol:"TKN", decimals:18})` to EVM Ethereum. Token is deployed at address `0xAAA`.
3. Attacker copies `(sig, payload)` from Ethereum calldata and calls `deployToken(sig, payload)` on EVM Arbitrum. The EVM Arbitrum bridge reconstructs the identical borsh bytes, recovers the same `nearBridgeDerivedAddress`, and accepts the call. Token is deployed at `0xBBB` on Arbitrum.
4. NEAR has no record of `0xBBB` on Arbitrum. It will never sign a `finTransfer` for `token.near` on Arbitrum.
5. When the relayer later tries to legitimately deploy `token.near` on Arbitrum, the call reverts: `require(!isBridgeToken[nearToEthToken[metadata.token]], "ERR_TOKEN_EXIST")` — the deployment path is permanently closed. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** near/omni-bridge/src/lib.rs (L345-354)
```rust
        let metadata_payload = MetadataPayload {
            prefix: PayloadType::Metadata,
            token: token_id.to_string(),
            name: metadata.name,
            symbol: metadata.symbol,
            decimals: metadata.decimals,
        };

        let payload = near_sdk::env::keccak256_array(
            borsh::to_vec(&metadata_payload).near_expect(BridgeError::Borsh),
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

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L289-313)
```text
        bytes memory borshEncoded = bytes.concat(
            bytes1(uint8(BridgeTypes.PayloadType.TransferMessage)),
            Borsh.encodeUint64(payload.destinationNonce),
            bytes1(payload.originChain),
            Borsh.encodeUint64(payload.originNonce),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(payload.tokenAddress),
            Borsh.encodeUint128(payload.amount),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(payload.recipient),
            bytes(payload.feeRecipient).length == 0 // None or Some(String) in rust
                ? bytes("\x00")
                : bytes.concat(
                    bytes("\x01"),
                    Borsh.encodeString(payload.feeRecipient)
                ),
            bytes(payload.message).length == 0
                ? bytes("")
                : Borsh.encodeBytes(payload.message)
        );
        bytes32 hashed = keccak256(borshEncoded);

        if (ECDSA.recover(hashed, signatureData) != nearBridgeDerivedAddress) {
            revert InvalidSignature();
        }
```

**File:** starknet/src/bridge_types.cairo (L36-44)
```text
    fn to_borsh(self: @MetadataPayload) -> ByteArray {
        let mut borsh_bytes: ByteArray = Default::default();
        borsh_bytes.append_byte(PayloadType::Metadata.into());
        borsh_bytes.append(@borsh::encode_byte_array(self.token));
        borsh_bytes.append(@borsh::encode_byte_array(self.name));
        borsh_bytes.append(@borsh::encode_byte_array(self.symbol));
        borsh_bytes.append_byte(*self.decimals);
        borsh_bytes
    }
```

**File:** starknet/src/bridge_types.cairo (L61-71)
```text
    fn to_borsh(self: @TransferMessagePayload, chain_id: u8) -> ByteArray {
        let mut borsh_bytes: ByteArray = Default::default();
        borsh_bytes.append_byte(PayloadType::TransferMessage.into());
        borsh_bytes.append(@borsh::encode_u64(*self.destination_nonce));
        borsh_bytes.append_byte(*self.origin_chain);
        borsh_bytes.append(@borsh::encode_u64(*self.origin_nonce));
        borsh_bytes.append_byte(chain_id);
        borsh_bytes.append(@borsh::encode_address(*self.token_address));
        borsh_bytes.append(@borsh::encode_u128(*self.amount));
        borsh_bytes.append_byte(chain_id);
        borsh_bytes.append(@borsh::encode_address(*self.recipient));
```

**File:** solana/programs/bridge_token_factory/src/state/message/deploy_token.rs (L19-26)
```rust
    fn serialize_for_near(&self, _params: Self::AdditionalParams) -> Result<Vec<u8>> {
        let mut writer = BufWriter::new(Vec::with_capacity(DEFAULT_SERIALIZER_CAPACITY));
        IncomingMessageType::Metadata.serialize(&mut writer)?;
        self.serialize(&mut writer)?; // borsh encoding
        writer
            .into_inner()
            .map_err(|_| error!(ErrorCode::InvalidArgs))
    }
```

**File:** aptos/sources/omni_bridge.move (L370-372)
```text
        let payload = bridge_types::new_metadata_payload(token, name, symbol, decimals);
        let encoded = payload.metadata_to_borsh();
        verify_signature(state, encoded, signature_rs, signature_v);
```

**File:** aptos/sources/omni_bridge.move (L450-451)
```text
        let encoded = payload.transfer_message_to_borsh(state.chain_id);
        verify_signature(state, encoded, signature_rs, signature_v);
```
