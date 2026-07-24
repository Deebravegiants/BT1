### Title
`MetadataPayload` Signature Lacks Chain ID Binding — Cross-Chain Replay of `deploy_token` Permanently Blocks Legitimate Token Deployment - (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

The `deploy_token` / `MetadataPayload` signature hash does not include any chain identifier. A valid NEAR MPC signature authorizing token deployment on one chain is cryptographically identical on every other chain. An unprivileged attacker who observes a `deploy_token` transaction on chain A can replay the same `(signatureData, MetadataPayload)` tuple on chains B, C, D, … permanently occupying the token slot on those chains and making legitimate deployment impossible.

---

### Finding Description

Every `fin_transfer` path correctly binds the signed hash to the destination chain by interleaving `omniBridgeChainId` / `chain_id` / `SOLANA_OMNI_BRIDGE_CHAIN_ID` into the Borsh-encoded payload before hashing:

**EVM** (`OmniBridge.sol` lines 289–309):
```solidity
bytes1(omniBridgeChainId),   // before tokenAddress
...
bytes1(omniBridgeChainId),   // before recipient
```

**Starknet** (`omni_bridge.cairo` line 253):
```cairo
@payload.to_borsh(self.omni_bridge_chain_id.read())
```

**Aptos** (`omni_bridge.move` line 450 / `bridge_types.move` lines 127, 130):
```move
buf.push_back(chain_id);  // before token_address
...
buf.push_back(chain_id);  // before recipient
```

**Solana** (`finalize_transfer.rs` lines 30, 35):
```rust
writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;  // before mint
...
writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;  // before recipient
```

The `deploy_token` / `MetadataPayload` path omits this binding on **every** chain:

**EVM** (`OmniBridge.sol` lines 142–149):
```solidity
bytes memory borshEncoded = bytes.concat(
    bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
    Borsh.encodeString(metadata.token),
    Borsh.encodeString(metadata.name),
    Borsh.encodeString(metadata.symbol),
    bytes1(metadata.decimals)
    // ← no omniBridgeChainId
);
```

**Starknet** (`bridge_types.cairo` lines 36–44):
```cairo
fn to_borsh(self: @MetadataPayload) -> ByteArray {
    borsh_bytes.append_byte(PayloadType::Metadata.into());
    borsh_bytes.append(@borsh::encode_byte_array(self.token));
    borsh_bytes.append(@borsh::encode_byte_array(self.name));
    borsh_bytes.append(@borsh::encode_byte_array(self.symbol));
    borsh_bytes.append_byte(*self.decimals);
    // ← no chain_id
}
```

**Aptos** (`bridge_types.move` lines 105–113):
```move
public fun metadata_to_borsh(self: &MetadataPayload): vector<u8> {
    buf.push_back(PAYLOAD_TYPE_METADATA);
    buf.append(borsh::encode_string(&self.token));
    buf.append(borsh::encode_string(&self.name));
    buf.append(borsh::encode_string(&self.symbol));
    buf.push_back(self.decimals);
    // ← no chain_id
}
```

**Solana** (`deploy_token.rs` lines 19–27):
```rust
fn serialize_for_near(&self, _params: Self::AdditionalParams) -> Result<Vec<u8>> {
    IncomingMessageType::Metadata.serialize(&mut writer)?;
    self.serialize(&mut writer)?;
    // ← no SOLANA_OMNI_BRIDGE_CHAIN_ID
}
```

Because `nearBridgeDerivedAddress` / `near_bridge_derived_address` / `derived_near_bridge_address` is the same NEAR MPC-derived key across all chains, the recovered signer check passes identically on every chain for the same payload bytes.

---

### Impact Explanation

When NEAR MPC signs a `MetadataPayload` for token `"foo.near"` targeting chain A, the resulting `(signature, payload)` pair is valid on chains B, C, D, … without modification. An attacker who replays it:

1. Deploys `"foo.near"` on chain B without NEAR's authorization for that chain.
2. Permanently occupies the token slot: all four chains guard against re-deployment (`ERR_TOKEN_EXIST` / `ERR_TOKEN_ALREADY_DEPLOYED` / `E_TOKEN_ALREADY_DEPLOYED`).
3. NEAR's internal state has no record of the deployment on chain B, so it will never sign `fin_transfer` payloads for that token on chain B.
4. Any user who later initiates a bridge transfer of `"foo.near"` toward chain B will have their tokens locked on NEAR with no redemption path — a permanent, irreversible fund lock.

This satisfies: **Irreversible fund lock / frozen redemption path** and **asset-identity / token-mapping divergence that breaks backing guarantees**.

---

### Likelihood Explanation

- `deploy_token` is a public, permissionless entry point on all four chains.
- The submitted `signatureData` is visible in the transaction calldata the moment it is included in a block on chain A.
- Replaying it on chain B requires only constructing a transaction with the same arguments — no privileged access, no leaked key, no colluding party.
- The attacker can target any token that NEAR has ever signed a `deploy_token` payload for, across all supported chains simultaneously.

---

### Recommendation

Include the destination chain identifier in the `MetadataPayload` Borsh encoding before hashing, mirroring the pattern already used in `TransferMessagePayload`:

**EVM:**
```solidity
bytes memory borshEncoded = bytes.concat(
    bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
+   bytes1(omniBridgeChainId),
    Borsh.encodeString(metadata.token),
    ...
);
```

**Starknet:**
```cairo
fn to_borsh(self: @MetadataPayload, chain_id: u8) -> ByteArray {
    borsh_bytes.append_byte(PayloadType::Metadata.into());
+   borsh_bytes.append_byte(chain_id);
    ...
}
```

**Aptos:**
```move
public fun metadata_to_borsh(self: &MetadataPayload, chain_id: u8): vector<u8> {
    buf.push_back(PAYLOAD_TYPE_METADATA);
+   buf.push_back(chain_id);
    ...
}
```

**Solana:**
```rust
fn serialize_for_near(&self, _params: Self::AdditionalParams) -> Result<Vec<u8>> {
    IncomingMessageType::Metadata.serialize(&mut writer)?;
+   writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
    self.serialize(&mut writer)?;
}
```

The NEAR MPC signing service must also include the target chain ID when constructing the payload to sign, so that signatures are chain-scoped from the point of creation.

---

### Proof of Concept

1. NEAR MPC signs `MetadataPayload { token: "usdc.near", name: "USD Coin", symbol: "USDC", decimals: 6 }` for EVM Ethereum (`omniBridgeChainId = 1`). The Borsh-encoded bytes are `[0x01, 0x09, 0x00, 0x00, 0x00, "usdc.near", ...]`.

2. The relayer submits `deployToken(sig, payload)` on Ethereum. The transaction is mined; `sig` is now public in calldata.

3. Attacker copies `sig` and `payload` verbatim and calls `deployToken(sig, payload)` on EVM Arbitrum (`omniBridgeChainId = 2`). The hash verified is `keccak256([0x01, 0x09, 0x00, 0x00, 0x00, "usdc.near", ...])` — byte-identical to Ethereum. `ECDSA.recover` returns `nearBridgeDerivedAddress`. The check passes. `"usdc.near"` is deployed on Arbitrum.

4. Attacker repeats for Starknet, Aptos, and Solana using the same `sig`.

5. NEAR has no record of these deployments. When NEAR later attempts to legitimately deploy `"usdc.near"` on Arbitrum, the on-chain call reverts with `ERR_TOKEN_EXIST`. NEAR cannot finalize transfers of `"usdc.near"` to Arbitrum. All user funds bridged toward Arbitrum for this token are permanently locked.

---

**Affected files:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L142-149)
```text
        bytes memory borshEncoded = bytes.concat(
            bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
            Borsh.encodeString(metadata.token),
            Borsh.encodeString(metadata.name),
            Borsh.encodeString(metadata.symbol),
            bytes1(metadata.decimals)
        );
        bytes32 hashed = keccak256(borshEncoded);
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

**File:** aptos/sources/bridge_types.move (L105-113)
```text
    public fun metadata_to_borsh(self: &MetadataPayload): vector<u8> {
        let buf = vector[];
        buf.push_back(PAYLOAD_TYPE_METADATA);
        buf.append(borsh::encode_string(&self.token));
        buf.append(borsh::encode_string(&self.name));
        buf.append(borsh::encode_string(&self.symbol));
        buf.push_back(self.decimals);
        buf
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
