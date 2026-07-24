### Title
Cross-Chain Replay of `deploy_token` Signatures Due to Missing Chain-ID Binding in `MetadataPayload` Borsh Encoding — (File: `starknet/src/bridge_types.cairo`, `evm/src/omni-bridge/contracts/OmniBridge.sol`, `aptos/sources/bridge_types.move`)

---

### Summary

The `MetadataPayload` Borsh encoding used for `deploy_token` signature verification omits any destination chain identifier. Because the same NEAR MPC–derived Ethereum address (`nearBridgeDerivedAddress`) is used across every supported chain, a single valid `deploy_token` signature produced for chain A is cryptographically identical and accepted on chain B, C, or any other deployed chain. An unprivileged attacker who observes a valid signature on-chain can replay it on any other chain to deploy the same token without NEAR authorization, then register the resulting token mapping on NEAR via `bind_token`.

---

### Finding Description

**Root cause — missing chain-id in `MetadataPayload` Borsh encoding**

`TransferMessagePayload.to_borsh()` correctly embeds `chain_id` twice (as the OmniAddress tag before `token_address` and before `recipient`), binding the signed hash to the destination chain. `MetadataPayload.to_borsh()` does not include any chain identifier:

Starknet: [1](#0-0) 

EVM: [2](#0-1) 

Aptos: [3](#0-2) 

All three produce the identical byte sequence: `[0x01 | token_borsh | name_borsh | symbol_borsh | decimals]`. No chain discriminator is present.

**Same derived address on every chain**

Every chain verifies the recovered ECDSA signer against the same NEAR MPC–derived Ethereum address. The NEAR bridge uses a single constant derivation path: [4](#0-3) 

The resulting 20-byte address is stored identically on EVM (`nearBridgeDerivedAddress`), Starknet (`omni_bridge_derived_address`), and Aptos (`near_bridge_derived_address`). Signature recovery on all three chains uses `keccak256(borsh(MetadataPayload))` against this same address:

EVM recovery: [5](#0-4) 

Starknet recovery: [6](#0-5) 

Aptos recovery: [7](#0-6) 

**Exploit flow**

1. NEAR MPC signs `MetadataPayload{token="usdc.near", name="USD Coin", symbol="USDC", decimals=6}` for Ethereum. The signature is publicly visible in the Ethereum transaction.
2. Attacker submits the identical `(signatureData, metadata)` to `deployToken()` on Abstract (or Starknet, or Aptos). The hash is identical; the derived address is identical; the call succeeds.
3. The target chain emits a `DeployToken` event from its registered factory address.
4. Attacker calls `bind_token` on NEAR with a proof of that event. NEAR's `bind_token_callback` checks only that `emitter_address` matches the registered factory for that chain: [8](#0-7) 
5. NEAR inserts a new `(chain_B, "usdc.near")` entry into `locked_tokens` and registers the token address mapping: [9](#0-8) 

The token is now registered on NEAR for chain B without any authorization from the NEAR bridge operator.

---

### Impact Explanation

**Category:** High — Acceptance of insufficiently-bound signatures that bypass execution gates.

The execution gate being bypassed is the chain-specific authorization for token deployment. A `deploy_token` signature is intended to authorize deployment on exactly one chain; the missing chain-id binding makes it a universal authorization for all chains simultaneously.

Concrete consequences:
- An attacker can register any NEAR token ID for any chain where the bridge is deployed, without operator approval.
- If the legitimate deployment for chain B has not yet occurred, the attacker's registration occupies the `(chain_B, token)` slot in `locked_tokens`. The subsequent legitimate `bind_token` call will fail with `TokenAlreadyLocked`, permanently blocking the authorized deployment path for that token on that chain.
- Once registered, the token can participate in bridge flows (init/fin transfer) on chain B, creating token accounting entries on NEAR that were never authorized.

---

### Likelihood Explanation

**Medium.** Every `deploy_token` transaction on any chain exposes the signature in calldata. Any observer can extract it and replay it on any other chain where the bridge is deployed and the token has not yet been registered. No privileged access, leaked key, or off-chain coordination is required. The only constraint is that the target chain must have a registered factory on NEAR, which is true for all production deployments.

---

### Recommendation

Bind the destination chain identifier into the `MetadataPayload` Borsh encoding, mirroring the pattern already used in `TransferMessagePayload`:

```
[type_byte | chain_id | token_borsh | name_borsh | symbol_borsh | decimals]
```

This must be applied consistently across all three implementations (EVM, Starknet, Aptos) and the NEAR-side signing logic. The `chain_id` value should be the same `omni_bridge_chain_id` / `chainId` already stored in each contract's state.

---

### Proof of Concept

1. Deploy the Omni Bridge on two EVM chains, chain A (e.g., Ethereum, `chainId=1`) and chain B (e.g., Abstract, `chainId=2`), both with registered factories on NEAR.
2. Trigger `log_metadata` on chain A for token `T`. NEAR MPC signs `MetadataPayload{token="T", name="Token", symbol="TKN", decimals=18}` and the signature is submitted to chain A's `deployToken()`. Observe the `(signatureData, metadata)` in the transaction.
3. Submit the identical `(signatureData, metadata)` to chain B's `deployToken()`. The call succeeds because `keccak256(borsh(MetadataPayload))` is chain-agnostic and `nearBridgeDerivedAddress` is identical on both chains.
4. Chain B emits `DeployToken(tokenAddress_B, "T", ...)`.
5. Call `bind_token` on NEAR with an MPC proof of chain B's `DeployToken` event. NEAR's `bind_token_callback` accepts it (factory check passes) and inserts `(ChainB, "T") → 0` into `locked_tokens`.
6. Token `T` is now registered on NEAR for chain B without operator authorization. Any subsequent legitimate `bind_token` for `(ChainB, "T")` will revert with `TokenAlreadyLocked`.

### Citations

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

**File:** near/omni-bridge/src/lib.rs (L84-84)
```rust
const SIGN_PATH: &str = "bridge-1";
```

**File:** near/omni-bridge/src/lib.rs (L1257-1262)
```rust
        require!(
            self.factories
                .get(&deploy_token.emitter_address.get_chain())
                == Some(deploy_token.emitter_address),
            BridgeError::UnknownFactory.as_ref()
        );
```

**File:** near/omni-bridge/src/lib.rs (L1266-1284)
```rust
        self.add_token(
            &deploy_token.token,
            &deploy_token.token_address,
            deploy_token.decimals,
            deploy_token.origin_decimals,
        );

        require!(
            self.locked_tokens
                .insert(
                    &(
                        deploy_token.token_address.get_chain(),
                        deploy_token.token.clone(),
                    ),
                    &0,
                )
                .is_none(),
            TokenLockError::TokenAlreadyLocked.as_ref()
        );
```

**File:** starknet/src/omni_bridge.cairo (L398-406)
```text
    fn _verify_borsh_signature(
        ref self: ContractState, borsh_bytes: @ByteArray, signature: Signature,
    ) {
        let message_hash_le = compute_keccak_byte_array(borsh_bytes);
        let message_hash = reverse_u256_bytes(message_hash_le);

        let sig = signature_from_vrs(signature.v, signature.r, signature.s);
        verify_eth_signature(message_hash, sig, self.omni_bridge_derived_address.read());
    }
```

**File:** aptos/sources/utils.move (L36-60)
```text
    public fun verify_eth_signature(
        message_bytes: vector<u8>,
        signature_rs: vector<u8>,
        v: u8,
        expected_address: vector<u8>
    ) {
        assert!(signature_rs.length() == 64, E_INVALID_SIGNATURE_LENGTH);
        assert!(expected_address.length() == 20, E_INVALID_SIGNATURE);

        let message_hash = aptos_hash::keccak256(message_bytes);

        let recovery_id = if (v >= 27) { v - 27 }
        else { v };

        let sig = secp256k1::ecdsa_signature_from_bytes(signature_rs);
        let recovered = secp256k1::ecdsa_recover(message_hash, recovery_id, &sig);
        assert!(recovered.is_some(), E_RECOVER_FAILED);
        let pk = recovered.extract();
        let pk_bytes = secp256k1::ecdsa_raw_public_key_to_bytes(&pk);

        let pk_hash = aptos_hash::keccak256(pk_bytes);
        let addr = last_20_bytes(&pk_hash);

        assert!(addr == expected_address, E_INVALID_SIGNATURE);
    }
```
