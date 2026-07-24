### Title
MetadataPayload Signature Lacks Chain-ID Binding, Enabling Cross-Chain Replay of Token Deployment — (`evm/src/omni-bridge/contracts/OmniBridge.sol`, `starknet/src/omni_bridge.cairo`, `solana/programs/bridge_token_factory/src/state/message/deploy_token.rs`)

---

### Summary

The MPC-signed `MetadataPayload` used in `deployToken` / `deploy_token` does not include the destination chain ID in its hash. A single valid signature obtained from one chain can be replayed verbatim on every other chain where the bridge is deployed, bypassing the intended per-chain authorization gate and permanently locking out the protocol from deploying that token through the normal path on any replayed chain.

---

### Finding Description

Every `finTransfer` / `fin_transfer` hash includes `omniBridgeChainId` twice (once for the token address field, once for the recipient field), explicitly binding the signature to a single destination chain.

**EVM `finTransfer` (chain-bound):** [1](#0-0) 

```
bytes1(omniBridgeChainId),   // token chain
...
bytes1(omniBridgeChainId),   // recipient chain
```

**EVM `deployToken` (no chain binding):** [2](#0-1) 

```solidity
bytes memory borshEncoded = bytes.concat(
    bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
    Borsh.encodeString(metadata.token),
    Borsh.encodeString(metadata.name),
    Borsh.encodeString(metadata.symbol),
    bytes1(metadata.decimals)          // ← no chain ID anywhere
);
bytes32 hashed = keccak256(borshEncoded);
if (ECDSA.recover(hashed, signatureData) != nearBridgeDerivedAddress) revert InvalidSignature();
```

The same asymmetry exists on Starknet. `fin_transfer` passes `self.omni_bridge_chain_id.read()` into the borsh serializer, while `deploy_token` calls `payload.to_borsh()` with no chain argument: [3](#0-2) [4](#0-3) 

And on Solana, `DeployTokenPayload::serialize_for_near` writes only the `Metadata` prefix and the payload fields — no `SOLANA_OMNI_BRIDGE_CHAIN_ID` — while `FinalizeTransferPayload::serialize_for_near` writes `SOLANA_OMNI_BRIDGE_CHAIN_ID` for both the token and recipient fields: [5](#0-4) [6](#0-5) 

The `MetadataPayload` struct itself contains no chain field: [7](#0-6) 

---

### Impact Explanation

An attacker who observes a legitimate `deployToken` transaction on chain A (e.g., Ethereum) extracts the `(signatureData, MetadataPayload)` tuple from the calldata. Because the hash contains no chain ID, the identical tuple is accepted by the bridge contracts on every other chain (Arbitrum, Starknet, Solana, etc.).

On each replayed chain the bridge contract:
1. Verifies the signature — passes, because the hash is identical.
2. Deploys a wrapped token and writes `nearToEthToken[metadata.token]` / equivalent mapping.
3. Sets `isBridgeToken[bridgeTokenProxy] = true`.

After the replay, the guard `require(!isBridgeToken[nearToEthToken[metadata.token]], "ERR_TOKEN_EXIST")` permanently blocks the protocol from ever deploying that token on the replayed chain through the normal path. [8](#0-7) 

The attacker-deployed token is at a nonce-dependent address that the NEAR bridge did not record. When NEAR later tries to finalize transfers to that chain for the same token, it will reference a different (unregistered) address, causing all inbound transfers for that token on that chain to fail permanently — an irreversible fund-lock / frozen redemption path.

---

### Likelihood Explanation

- The attacker needs only to watch the public mempool or finalized blocks on any one chain for a `deployToken` call.
- No privileged access, leaked key, or MPC compromise is required.
- The replay is a single public transaction on any target chain.
- The bridge is deployed on multiple EVM chains, Starknet, and Solana simultaneously, so every new token deployment is immediately replayable across all of them.

Likelihood: **High**.

---

### Recommendation

Include the destination chain ID in the `MetadataPayload` borsh encoding before hashing, mirroring the pattern already used in `finTransfer`:

**EVM:**
```solidity
bytes memory borshEncoded = bytes.concat(
    bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
+   bytes1(omniBridgeChainId),
    Borsh.encodeString(metadata.token),
    Borsh.encodeString(metadata.name),
    Borsh.encodeString(metadata.symbol),
    bytes1(metadata.decimals)
);
```

Apply the equivalent fix in `starknet/src/bridge_types.cairo` (`MetadataPayload::to_borsh`) and in `solana/programs/bridge_token_factory/src/state/message/deploy_token.rs` (`DeployTokenPayload::serialize_for_near`). The NEAR MPC signer must include the target chain ID when constructing the payload to sign.

---

### Proof of Concept

1. Protocol deploys token `foo.near` on Ethereum. Transaction is mined; calldata `(sig, MetadataPayload{token:"foo.near", name:"Foo", symbol:"FOO", decimals:18})` is public.
2. Attacker calls `deployToken(sig, MetadataPayload{...})` on the Arbitrum `OmniBridge` with the identical arguments.
3. `keccak256(borshEncoded)` is identical on both chains (no chain ID in the hash). `ECDSA.recover` returns `nearBridgeDerivedAddress`. Signature check passes.
4. `foo.near` wrapped token is deployed on Arbitrum at a nonce-determined address `X`. Mapping `nearToEthToken["foo.near"] = X` is written.
5. Protocol later attempts to deploy `foo.near` on Arbitrum via the normal flow. The call reverts with `ERR_TOKEN_EXIST`.
6. NEAR bridge records a different address for Arbitrum (or none). All `finTransfer` calls for `foo.near` on Arbitrum reference the wrong token address, permanently freezing user funds that bridge to Arbitrum for that token.

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

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L289-309)
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
```

**File:** starknet/src/omni_bridge.cairo (L202-210)
```text
        fn deploy_token(ref self: ContractState, signature: Signature, payload: MetadataPayload) {
            assert(!_is_paused(@self, PAUSE_DEPLOY_TOKEN), 'ERR_DEPLOY_TOKEN_PAUSED');

            _verify_borsh_signature(ref self, @payload.to_borsh(), signature);

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

**File:** near/omni-types/src/lib.rs (L714-722)
```rust
#[near(serializers = [borsh, json])]
#[derive(Debug, Clone)]
pub struct MetadataPayload {
    pub prefix: PayloadType,
    pub token: String,
    pub name: String,
    pub symbol: String,
    pub decimals: u8,
}
```
