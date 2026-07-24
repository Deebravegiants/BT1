### Title
Cross-Chain Signature Replay in `deployToken` / `deploy_token` Due to Missing Chain ID in Metadata Payload Hash — (Files: `evm/src/omni-bridge/contracts/OmniBridge.sol`, `starknet/src/bridge_types.cairo`, `solana/programs/bridge_token_factory/src/state/message/deploy_token.rs`, `aptos/sources/bridge_types.move`)

---

### Summary

The NEAR MPC-signed `MetadataPayload` used by `deployToken` / `deploy_token` across all destination chains (EVM, Starknet, Solana, Aptos) does **not** include the destination chain ID in the hashed message. A single valid MPC signature obtained from a `deployToken` call on one chain can be replayed verbatim on every other chain to deploy the same wrapped token without a new MPC authorization. By contrast, `finTransfer` / `fin_transfer` correctly binds the chain ID into the signed hash on all four chains, making this asymmetry a clear design gap in the `deployToken` path.

---

### Finding Description

**`finTransfer` (protected):** Every chain encodes the destination chain ID into the Borsh hash before signature verification. For example, EVM encodes `bytes1(omniBridgeChainId)` twice (for token address and recipient), Starknet passes `chain_id` into `to_borsh(chain_id)`, Solana writes `SOLANA_OMNI_BRIDGE_CHAIN_ID` before each address field, and Aptos calls `transfer_message_to_borsh(state.chain_id)`.

**`deployToken` (unprotected):** The `MetadataPayload` Borsh encoding on every chain is identical and contains only `[PayloadType::Metadata, token, name, symbol, decimals]` — no chain ID anywhere.

EVM (`OmniBridge.sol`):
```solidity
bytes memory borshEncoded = bytes.concat(
    bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
    Borsh.encodeString(metadata.token),
    Borsh.encodeString(metadata.name),
    Borsh.encodeString(metadata.symbol),
    bytes1(metadata.decimals)          // ← no chain ID
);
bytes32 hashed = keccak256(borshEncoded);
if (ECDSA.recover(hashed, signatureData) != nearBridgeDerivedAddress) revert InvalidSignature();
```

Starknet (`bridge_types.cairo`, `MetadataPayloadImpl::to_borsh`):
```cairo
fn to_borsh(self: @MetadataPayload) -> ByteArray {
    borsh_bytes.append_byte(PayloadType::Metadata.into());
    borsh_bytes.append(@borsh::encode_byte_array(self.token));
    borsh_bytes.append(@borsh::encode_byte_array(self.name));
    borsh_bytes.append(@borsh::encode_byte_array(self.symbol));
    borsh_bytes.append_byte(*self.decimals);  // ← no chain ID
    borsh_bytes
}
```

Solana (`deploy_token.rs`, `DeployTokenPayload::serialize_for_near`):
```rust
IncomingMessageType::Metadata.serialize(&mut writer)?;
self.serialize(&mut writer)?;  // token, name, symbol, decimals — no chain ID
```

Aptos (`bridge_types.move`, `metadata_to_borsh`):
```move
buf.push_back(PAYLOAD_TYPE_METADATA);
buf.append(borsh::encode_string(&self.token));
buf.append(borsh::encode_string(&self.name));
buf.append(borsh::encode_string(&self.symbol));
buf.push_back(self.decimals);  // ← no chain ID
```

Because the four chains produce byte-identical hashes for the same token metadata, a single MPC signature is simultaneously valid on all of them.

---

### Impact Explanation

An unprivileged attacker who observes a legitimate `deployToken` transaction on chain A can extract the signature and submit it to `deployToken` on chains B, C, and D. Each chain will accept it (signature recovers to `nearBridgeDerivedAddress`), deploy a wrapped token, and register it in the local `nearToEthToken` / `near_to_starknet_token` / `near_to_aptos_token` mapping.

Concrete harms:

1. **Unauthorized token deployment on chains the NEAR bridge has not yet authorized.** The NEAR bridge signs a metadata payload only when it decides to support a token on a specific chain. Replaying that signature forces deployment on every other chain regardless of NEAR's readiness.

2. **Permanent DoS of legitimate future deployment.** Each chain enforces a one-time-only guard (`ERR_TOKEN_EXIST` on EVM, `ERR_TOKEN_ALREADY_DEPLOYED` on Starknet, equivalent checks on Solana/Aptos). Once the attacker deploys the token on chain B, the NEAR bridge can never deploy it again on chain B through the normal path. If the NEAR bridge later tries to authorize chain B for that token, the call reverts, permanently blocking the token on that chain.

3. **State divergence between NEAR and destination chains.** The NEAR bridge may pick up the spurious `DeployToken` events and register incorrect or premature token addresses, corrupting its internal routing tables for subsequent `finTransfer` operations.

This fits the allowed impact: **insufficiently-bound signatures that bypass execution gates** and **asset-identity / token-mapping divergence that breaks backing guarantees**.

---

### Likelihood Explanation

- All `deployToken` transactions are public on-chain; the signature is trivially extractable from calldata.
- The attacker needs no privileged access, no leaked key, and no colluding party.
- The replay works on any chain that shares the same `nearBridgeDerivedAddress` (all four do by design).
- The only timing constraint is that the attacker must act before the NEAR bridge itself deploys the token on the target chain — a window that can be hours to days.

Likelihood: **Medium-High**.

---

### Recommendation

Include the destination chain ID in the `MetadataPayload` Borsh encoding, mirroring the pattern already used by `TransferMessagePayload`. Concretely:

- **EVM**: add `bytes1(omniBridgeChainId)` to the `borshEncoded` concatenation in `deployToken`.
- **Starknet**: change `to_borsh(self: @MetadataPayload)` to `to_borsh(self: @MetadataPayload, chain_id: u8)` and append `chain_id`.
- **Solana**: add `writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;` in `DeployTokenPayload::serialize_for_near`.
- **Aptos**: add `buf.push_back(state.chain_id)` in `metadata_to_borsh`.

The NEAR MPC signer must correspondingly include the target chain ID when constructing the payload to sign, so that signatures are chain-specific.

---

### Proof of Concept

1. NEAR MPC signs `keccak256(Borsh(Metadata, "token.near", "Token", "TKN", 18))` to authorize deployment on EVM (chain ID 1). The signature `sig` is broadcast in the EVM `deployToken` calldata.

2. Attacker reads `sig` from the EVM transaction.

3. Attacker calls Starknet `deploy_token(sig, MetadataPayload{"token.near","Token","TKN",18})`. Starknet computes `keccak256(Borsh(Metadata, "token.near", "Token", "TKN", 18))` — byte-identical to the EVM hash — and `verify_eth_signature` succeeds. The token is deployed on Starknet without NEAR's authorization.

4. Attacker repeats for Solana and Aptos using the same `sig`.

5. NEAR bridge later attempts to deploy "token.near" on Starknet; the call reverts with `ERR_TOKEN_ALREADY_DEPLOYED`. The token is permanently undeployable through the authorized path on Starknet.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

**Contrast with the protected `finTransfer` path:** [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

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

**File:** starknet/src/bridge_types.cairo (L61-84)
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
        match self.fee_recipient {
            Option::None => { borsh_bytes.append_byte(0); },
            Option::Some(fee_recipient) => {
                borsh_bytes.append_byte(1);
                borsh_bytes.append(@borsh::encode_byte_array(fee_recipient));
            },
        }
        match self.message {
            Option::None => {},
            Option::Some(message) => { borsh_bytes.append(@borsh::encode_byte_array(message)); },
        }
        borsh_bytes
    }
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

**File:** aptos/sources/bridge_types.move (L119-150)
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

        if (self.fee_recipient.is_some()) {
            buf.push_back(1);
            let fr = *self.fee_recipient.borrow();
            buf.append(borsh::encode_string(&fr));
        } else {
            buf.push_back(0);
        };

        // Note: matches Starknet — `message` is NOT wrapped in an Option
        // byte tag. None contributes nothing; Some(bytes) contributes only
        // the length-prefixed bytes.
        if (self.message.is_some()) {
            let msg = *self.message.borrow();
            buf.append(borsh::encode_byte_vec(&msg));
        };

        buf
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
