### Title
`deployToken` signed hash omits destination chain ID, enabling cross-chain signature replay — (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`)

---

### Summary

Every Omni Bridge chain (EVM, Solana, Starknet, Aptos) verifies a NEAR MPC ECDSA signature over a Borsh-encoded `MetadataPayload` in `deployToken`. That payload encodes only `(type_tag | token | name | symbol | decimals)` — **no destination chain ID**. The same signature is therefore valid on every chain simultaneously. In contrast, `finTransfer` on every chain correctly binds the destination chain ID into the signed hash. An unprivileged attacker who observes a legitimate `deployToken` transaction on chain A can replay the identical `(signatureData, metadata)` call on chain B, deploying the token there without any NEAR MPC authorization for chain B.

---

### Finding Description

**Asymmetry between `deployToken` and `finTransfer` hash construction — present on all chains:**

**EVM — `OmniBridge.sol`**

`deployToken` (lines 142–149) hashes:
```
keccak256( PayloadType.Metadata | token | name | symbol | decimals )
```
No chain ID. [1](#0-0) 

`finTransfer` (lines 289–311) hashes:
```
keccak256( PayloadType.TransferMessage | destinationNonce | originChain | originNonce |
           omniBridgeChainId | tokenAddress | amount | omniBridgeChainId | recipient | ... )
```
Chain ID bound twice. [2](#0-1) 

**Solana — `deploy_token.rs`**

`DeployTokenPayload::serialize_for_near` serializes `IncomingMessageType::Metadata | token | name | symbol | decimals` — no chain ID. [3](#0-2) 

`FinalizeTransferPayload::serialize_for_near` writes `SOLANA_OMNI_BRIDGE_CHAIN_ID` before both the token mint and the recipient pubkey. [4](#0-3) 

**Starknet — `omni_bridge.cairo`**

`deploy_token` calls `_verify_borsh_signature(ref self, @payload.to_borsh(), signature)` — `to_borsh()` takes no chain ID argument. [5](#0-4) 

`fin_transfer` calls `_verify_borsh_signature(ref self, @payload.to_borsh(self.omni_bridge_chain_id.read()), signature)` — chain ID is passed. [6](#0-5) 

**Aptos — `bridge_types.move`**

`metadata_to_borsh` encodes `(PAYLOAD_TYPE_METADATA | token | name | symbol | decimals)` — no chain ID parameter exists. [7](#0-6) 

`transfer_message_to_borsh` accepts an explicit `chain_id: u8` and writes it before both `token_address` and `recipient`. [8](#0-7) 

The code comment on `transfer_message_to_borsh` even documents the intent — "`chain_id` is interleaved … bound into the signed hash … preventing cross-chain replay" — but this protection was never applied to `metadata_to_borsh`. [9](#0-8) 

---

### Impact Explanation

**High — Acceptance of cross-domain signatures that bypass execution gates.**

A single NEAR MPC signature authorizing `deployToken` for token `T` on chain A is simultaneously valid on chains B, C, and D. An attacker can:

1. Observe a legitimate `deployToken(sig, metadata)` transaction on chain A (e.g., Ethereum).
2. Submit the identical call on chain B (e.g., Solana) before NEAR MPC has authorized deployment there.
3. The token is deployed on chain B under attacker-controlled timing, without NEAR MPC ever signing for chain B.

**Secondary DoS path**: Once the token is registered on chain B via replay (`nearToEthToken[metadata.token]` is set on EVM; `near_to_starknet_token` on Starknet; `near_to_aptos_token` on Aptos), any subsequent legitimate `deployToken` call from NEAR for that token on chain B reverts with `ERR_TOKEN_EXIST` / `ERR_TOKEN_ALREADY_DEPLOYED` / `E_TOKEN_ALREADY_DEPLOYED`. If NEAR's off-chain indexer does not detect and reconcile the replayed deployment, the token becomes permanently un-bridgeable to chain B — an irreversible fund-lock for that asset on that chain. [10](#0-9) [11](#0-10) 

---

### Likelihood Explanation

**Medium.** The attacker requires no privileges — `deployToken` is a public entry point on every chain. The only prerequisite is observing a valid `deployToken` transaction on any one chain (trivially done by monitoring public mempool or block explorers) and submitting the same calldata on another chain before the NEAR indexer reconciles the state. The attack window is the time between NEAR MPC signing for chain A and NEAR MPC signing for chain B, which can be hours to days for newly supported chains.

---

### Recommendation

Bind the destination chain ID into the `MetadataPayload` Borsh hash for `deployToken`, exactly as `finTransfer` already does. The chain ID should be read from the contract's stored `omniBridgeChainId` / `omni_bridge_chain_id` / `chain_id` state variable (not a constructor-time constant), consistent with the existing pattern.

**EVM diff:**
```diff
 bytes memory borshEncoded = bytes.concat(
     bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
+    bytes1(omniBridgeChainId),
     Borsh.encodeString(metadata.token),
     Borsh.encodeString(metadata.name),
     Borsh.encodeString(metadata.symbol),
     bytes1(metadata.decimals)
 );
```

Apply the equivalent change to `metadata_to_borsh` / `to_borsh()` on Solana, Starknet, and Aptos, passing the stored chain ID as a parameter — mirroring the existing `transfer_message_to_borsh(chain_id)` pattern already present in all four implementations.

---

### Proof of Concept

1. NEAR MPC signs `MetadataPayload { token: "usdc.near", name: "USD Coin", symbol: "USDC", decimals: 6 }` for Ethereum deployment. Signature `sig` is broadcast on Ethereum mainnet.
2. Attacker reads `sig` and `metadata` from the Ethereum transaction.
3. Attacker calls `deployToken(sig, metadata)` on the Solana bridge (`finalize_transfer` program), Starknet bridge, and Aptos bridge.
4. All three calls succeed: `ECDSA.recover(keccak256(borshEncoded), sig) == nearBridgeDerivedAddress` on EVM; equivalent secp256k1 recovery succeeds on Solana/Starknet/Aptos — because the hash is identical across all chains (no chain ID differentiates them).
5. `usdc.near` is now deployed on Solana, Starknet, and Aptos without NEAR MPC authorization for those chains.
6. When NEAR later attempts to legitimately deploy `usdc.near` on Starknet, the call reverts with `ERR_TOKEN_ALREADY_DEPLOYED`, permanently blocking the legitimate bridge path for USDC on Starknet.

### Citations

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

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L155-158)
```text
        require(
            !isBridgeToken[nearToEthToken[metadata.token]],
            "ERR_TOKEN_EXIST"
        );
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L289-312)
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

**File:** solana/programs/bridge_token_factory/src/state/message/finalize_transfer.rs (L29-36)
```rust
        // 3. token
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.0.serialize(&mut writer)?;
        // 4. amount
        self.amount.serialize(&mut writer)?;
        // 5. recipient
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.1.serialize(&mut writer)?;
```

**File:** starknet/src/omni_bridge.cairo (L202-205)
```text
        fn deploy_token(ref self: ContractState, signature: Signature, payload: MetadataPayload) {
            assert(!_is_paused(@self, PAUSE_DEPLOY_TOKEN), 'ERR_DEPLOY_TOKEN_PAUSED');

            _verify_borsh_signature(ref self, @payload.to_borsh(), signature);
```

**File:** starknet/src/omni_bridge.cairo (L207-209)
```text
            let token_id_hash = compute_keccak_byte_array(@payload.token);
            let existing_token = self.near_to_starknet_token.read(token_id_hash);
            assert(existing_token.is_zero(), 'ERR_TOKEN_ALREADY_DEPLOYED');
```

**File:** starknet/src/omni_bridge.cairo (L252-254)
```text
            _verify_borsh_signature(
                ref self, @payload.to_borsh(self.omni_bridge_chain_id.read()), signature,
            );
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

**File:** aptos/sources/bridge_types.move (L115-118)
```text
    /// Borsh encoding of `TransferMessagePayload`. Byte-identical to
    /// Starknet / EVM. `chain_id` is interleaved as the OmniAddress tag
    /// before each of `token_address` and `recipient` and is bound into
    /// the signed hash (not the payload), preventing cross-chain replay.
```

**File:** aptos/sources/bridge_types.move (L119-131)
```text
    public fun transfer_message_to_borsh(
        self: &TransferMessagePayload, chain_id: u8
    ): vector<u8> {
        let buf = vector[];
        buf.push_back(PAYLOAD_TYPE_TRANSFER_MESSAGE);
        buf.append(bcs::to_bytes(&self.destination_nonce));
        buf.push_back(self.origin_chain);
        buf.append(bcs::to_bytes(&self.origin_nonce));
        buf.push_back(chain_id);
        buf.append(bcs::to_bytes(&self.token_address));
        buf.append(bcs::to_bytes(&self.amount));
        buf.push_back(chain_id);
        buf.append(bcs::to_bytes(&self.recipient));
```
