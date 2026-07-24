Now I have a complete picture of the payload encodings across all chains. Let me confirm the key finding:

### Title
`deploy_token` MetadataPayload Lacks Chain-ID Binding, Enabling Cross-Chain MPC Signature Replay — (File: `evm/src/omni-bridge/contracts/OmniBridge.sol`, `starknet/src/bridge_types.cairo`, `aptos/sources/bridge_types.move`, `solana/programs/bridge_token_factory/src/state/message/deploy_token.rs`)

---

### Summary

The borsh-encoded payload that the NEAR MPC signs for `deploy_token` contains no chain identifier on any destination chain. An unprivileged attacker who observes a valid `deploy_token` submission on one chain can replay the identical signature on every other chain, deploying the same bridge token there without the MPC ever authorizing that chain. By contrast, `fin_transfer` correctly embeds the chain ID twice in its payload, preventing the same replay. The asymmetry is a direct, reachable root cause in production code.

---

### Finding Description

Every chain's `deploy_token` path constructs a borsh message of the form:

```
[ PayloadType::Metadata (0x01) | token_id | name | symbol | decimals ]
```

**EVM** (`OmniBridge.sol` lines 142–148):
```solidity
bytes memory borshEncoded = bytes.concat(
    bytes1(uint8(BridgeTypes.PayloadType.Metadata)),
    Borsh.encodeString(metadata.token),
    Borsh.encodeString(metadata.name),
    Borsh.encodeString(metadata.symbol),
    bytes1(metadata.decimals)
);
``` [1](#0-0) 

**Starknet** (`bridge_types.cairo` lines 36–44):
```cairo
fn to_borsh(self: @MetadataPayload) -> ByteArray {
    borsh_bytes.append_byte(PayloadType::Metadata.into());
    borsh_bytes.append(@borsh::encode_byte_array(self.token));
    borsh_bytes.append(@borsh::encode_byte_array(self.name));
    borsh_bytes.append(@borsh::encode_byte_array(self.symbol));
    borsh_bytes.append_byte(*self.decimals);
``` [2](#0-1) 

**Aptos** (`bridge_types.move` lines 105–113):
```move
public fun metadata_to_borsh(self: &MetadataPayload): vector<u8> {
    buf.push_back(PAYLOAD_TYPE_METADATA);
    buf.append(borsh::encode_string(&self.token));
    buf.append(borsh::encode_string(&self.name));
    buf.append(borsh::encode_string(&self.symbol));
    buf.push_back(self.decimals);
``` [3](#0-2) 

**Solana** (`deploy_token.rs` lines 19–26):
```rust
fn serialize_for_near(&self, _params: Self::AdditionalParams) -> Result<Vec<u8>> {
    IncomingMessageType::Metadata.serialize(&mut writer)?;
    self.serialize(&mut writer)?; // token, name, symbol, decimals
``` [4](#0-3) 

None of these four encodings include a chain ID. The resulting keccak256 hash — and therefore the MPC signature — is **identical** across all chains for the same token.

Compare this with `fin_transfer`, which correctly interleaves `chain_id` as the OmniAddress discriminant before both `token_address` and `recipient`:

```solidity
bytes1(omniBridgeChainId),
Borsh.encodeAddress(payload.tokenAddress),
...
bytes1(omniBridgeChainId),
Borsh.encodeAddress(payload.recipient),
``` [5](#0-4) 

The same chain-ID interleaving appears in Starknet (`bridge_types.cairo` lines 67–71), Aptos (`bridge_types.move` lines 127–131), and Solana (`finalize_transfer.rs` lines 30–36). The protection exists for transfers but is absent for token deployment. [6](#0-5) [7](#0-6) [8](#0-7) 

---

### Impact Explanation

`deploy_token` is fully permissionless on every chain — the only authorization gate is the MPC signature check:

- EVM: `ECDSA.recover(hashed, signatureData) != nearBridgeDerivedAddress` [9](#0-8) 
- Starknet: `_verify_borsh_signature(ref self, @payload.to_borsh(), signature)` [10](#0-9) 
- Aptos: `verify_signature(state, encoded, signature_rs, signature_v)` [11](#0-10) 
- Solana: `data.verify_signature((), &ctx.accounts.common.config.derived_near_bridge_address)` [12](#0-11) 

Because the signed hash is chain-agnostic, a single MPC signature passes all four checks. An attacker who observes a `deploy_token` call on chain A can immediately replay it on chains B, C, and D. Each chain's "already deployed" guard only prevents a second deployment on the *same* chain; it provides no cross-chain protection. [13](#0-12) 

Concrete consequences:

1. **Unauthorized token deployment on unintended chains.** The MPC may have authorized deployment only on chain A. The attacker forces deployment on B/C/D before the MPC is ready to support those chains, permanently occupying the token slot (`near_to_aptos_token`, `near_to_starknet_token`, `nearToEthToken`, Solana mint PDA). The MPC can never re-deploy the token on those chains.

2. **Permanent disruption of the bridge for that token on the replayed chain.** Because the token is deployed without the MPC tracking it, no `fin_transfer` signatures will be issued for that chain. Any user who later initiates a transfer targeting that chain will have their funds locked on the source chain with no redemption path — matching the "Irreversible fund lock / permanently unclaimable user value" impact category.

---

### Likelihood Explanation

The attack requires no privilege, no key material, and no off-chain infrastructure. Any on-chain observer can extract the `(signatureData, metadata)` arguments from a confirmed `deployToken` transaction on one chain and submit them to another chain's bridge contract in a single transaction. The attack is executable the moment the first `deploy_token` for any token appears on any chain.

---

### Recommendation

Include the destination chain ID in the `MetadataPayload` borsh encoding, mirroring the pattern already used by `TransferMessagePayload`. For example, prepend or append `chain_id` to the serialized buffer in every chain's `metadata_to_borsh` / `to_borsh` / `serialize_for_near` implementation, and update the NEAR MPC signing logic to include the target chain ID when producing `deploy_token` signatures.

---

### Proof of Concept

1. Token `"usdc.near"` is deployed on EVM. The transaction calldata contains `(signatureData, {token:"usdc.near", name:"USD Coin", symbol:"USDC", decimals:6})`.
2. Attacker copies `signatureData` verbatim and calls `deploy_token(signatureData, payload)` on the Starknet bridge. The Starknet `_verify_borsh_signature` call computes `keccak256([0x01 | "usdc.near" | "USD Coin" | "USDC" | 0x06])` — identical to the EVM hash — and the signature passes.
3. `"usdc.near"` is now registered in `near_to_starknet_token` on Starknet. The MPC never authorized Starknet deployment and does not track it.
4. The same replay works against Aptos and Solana with the same signature.
5. When the MPC later attempts to legitimately deploy `"usdc.near"` on Starknet, the call reverts with `ERR_TOKEN_ALREADY_DEPLOYED`, permanently blocking the legitimate deployment path. [14](#0-13) [13](#0-12)

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

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L151-153)
```text
        if (ECDSA.recover(hashed, signatureData) != nearBridgeDerivedAddress) {
            revert InvalidSignature();
        }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L293-298)
```text
            Borsh.encodeUint64(payload.originNonce),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(payload.tokenAddress),
            Borsh.encodeUint128(payload.amount),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(payload.recipient),
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

**File:** starknet/src/bridge_types.cairo (L67-71)
```text
        borsh_bytes.append_byte(chain_id);
        borsh_bytes.append(@borsh::encode_address(*self.token_address));
        borsh_bytes.append(@borsh::encode_u128(*self.amount));
        borsh_bytes.append_byte(chain_id);
        borsh_bytes.append(@borsh::encode_address(*self.recipient));
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

**File:** aptos/sources/bridge_types.move (L127-131)
```text
        buf.push_back(chain_id);
        buf.append(bcs::to_bytes(&self.token_address));
        buf.append(bcs::to_bytes(&self.amount));
        buf.push_back(chain_id);
        buf.append(bcs::to_bytes(&self.recipient));
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

**File:** solana/programs/bridge_token_factory/src/state/message/finalize_transfer.rs (L30-36)
```rust
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.0.serialize(&mut writer)?;
        // 4. amount
        self.amount.serialize(&mut writer)?;
        // 5. recipient
        writer.write_all(&[SOLANA_OMNI_BRIDGE_CHAIN_ID])?;
        params.1.serialize(&mut writer)?;
```

**File:** starknet/src/omni_bridge.cairo (L205-205)
```text
            _verify_borsh_signature(ref self, @payload.to_borsh(), signature);
```

**File:** starknet/src/omni_bridge.cairo (L207-209)
```text
            let token_id_hash = compute_keccak_byte_array(@payload.token);
            let existing_token = self.near_to_starknet_token.read(token_id_hash);
            assert(existing_token.is_zero(), 'ERR_TOKEN_ALREADY_DEPLOYED');
```

**File:** aptos/sources/omni_bridge.move (L372-372)
```text
        verify_signature(state, encoded, signature_rs, signature_v);
```

**File:** aptos/sources/omni_bridge.move (L375-378)
```text
        assert!(
            !state.near_to_aptos_token.contains(token_id),
            E_TOKEN_ALREADY_DEPLOYED
        );
```

**File:** solana/programs/bridge_token_factory/src/lib.rs (L72-72)
```rust
        data.verify_signature((), &ctx.accounts.common.config.derived_near_bridge_address)?;
```
