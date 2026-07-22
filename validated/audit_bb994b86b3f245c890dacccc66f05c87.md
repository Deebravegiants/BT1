### Title
Validator ECDSA Private Key Stored Unredacted in Memory via `Debug` Derivation and Hardcoded Test Key Wired into Production Consensus Signing — (File: `crates/apollo_signature_manager/src/signature_manager.rs`)

---

### Summary

The production `create_signature_manager()` function unconditionally instantiates `LocalKeyStore::new_for_testing()`, which embeds a hardcoded ECDSA private key (`0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133`) directly in the binary. Every validator node running this code shares the same publicly-known signing key. Simultaneously, `PrivateKey` derives `Debug` with no redaction, so the raw key scalar is emitted whenever the `SignatureManager`, `LocalKeyStore`, or any error carrying the key is formatted with `{:?}` — replicating the "plaintext sensitive value in memory/logs" class of the seed report.

---

### Finding Description

**Step 1 — `PrivateKey` derives `Debug` with no redaction** [1](#0-0) 

`PrivateKey(pub Felt)` derives `Debug`, `Serialize`, and `Deserialize`. Any `{:?}` formatting of the type prints the raw 252-bit scalar.

**Step 2 — `LocalKeyStore` derives `Debug` and stores the key as a plain field** [2](#0-1) 

`LocalKeyStore` derives `Debug`. Because `PrivateKey` also derives `Debug`, `format!("{:?}", keystore)` emits the private key value.

**Step 3 — `SignatureManager<KS>` derives `Debug` with a public `keystore` field** [3](#0-2) 

`pub keystore: KS` is directly accessible and printed by the derived `Debug` impl, so `format!("{:?}", signature_manager)` leaks the private key.

**Step 4 — `new_for_testing()` embeds a hardcoded key and is the only constructor reachable from production** [4](#0-3) 

The only other constructor, `_new(private_key)`, is prefixed with `_` (dead code) and never called. The `new_for_testing()` path is the sole live constructor.

**Step 5 — `create_signature_manager()` calls `new_for_testing()` unconditionally** [5](#0-4) 

**Step 6 — `create_signature_manager()` is wired into the production node** [6](#0-5) 

When `signature_manager` execution mode is `LocalExecutionWithRemoteDisabled` or `LocalExecutionWithRemoteEnabled`, the node calls `create_signature_manager()`, which returns a `SignatureManager` holding the hardcoded test key.

**Step 7 — This key signs consensus precommit votes** [7](#0-6) 

`sign_precommit_vote(block_hash)` calls `self.keystore.get_key()` and signs with the hardcoded scalar. The resulting signature is used by the consensus engine to cast votes on proposed block hashes.

---

### Impact Explanation

Every validator node running this binary uses the identical private key `0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133`, which is publicly readable in the repository. An attacker can:

1. Derive the corresponding public key and impersonate any validator's precommit vote.
2. Forge `2f+1` precommit votes for an arbitrary block hash, driving consensus to commit a block the honest proposer never built.
3. Cause the sequencer to finalize a wrong `ProposalCommitment`, propagating an incorrect state root to L1.

This matches the **High** impact tier: *"Transaction conversion or signature/hash logic binds the wrong signer, hash, type, or executable payload."*

Additionally, because `PrivateKey` derives `Debug` with no redaction, any future `#[instrument]` annotation, panic message, or error log that formats `SignatureManager` or `LocalKeyStore` will emit the raw key scalar to structured logs — the direct Sequencer analog of the seed report's plaintext-in-memory class.

---

### Likelihood Explanation

The hardcoded key is in the public source tree. No special access, network position, or cryptographic capability is required. Any participant who can send consensus messages to the network can immediately forge votes. Likelihood: **High**.

---

### Recommendation

1. **Remove the hardcoded key from production.** Implement a proper `KeyStore` backed by an environment variable, HSM, or secrets manager. The dead `_new(private_key: PrivateKey)` constructor already has the right signature — wire it to a real secret source and gate `new_for_testing()` behind `#[cfg(test)]`.
2. **Redact `PrivateKey` in `Debug`.** Replace the derived `Debug` with a manual implementation that prints `PrivateKey(***)` to prevent accidental log leakage.
3. **Gate `LocalKeyStore` behind `#[cfg(test)]`.** The struct and its `new_for_testing()` constructor should not be reachable from production code paths.

---

### Proof of Concept

```
# 1. The hardcoded key is in the source:
#    crates/apollo_signature_manager/src/signature_manager.rs, line 103-104
#    PRIVATE_KEY = 0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133

# 2. Production call chain:
create_node_components()                          # components.rs:558
  -> create_signature_manager()                  # lib.rs:42
    -> LocalKeyStoreSignatureManager::new()       # lib.rs:19
      -> LocalKeyStore::new_for_testing()         # signature_manager.rs:101
        -> PRIVATE_KEY (hardcoded)

# 3. Forge a precommit vote for an arbitrary block hash:
use starknet_core::crypto::ecdsa_sign;
let private_key = Felt::from_hex_unchecked(
    "0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133"
);
let target_block_hash = /* any hash the attacker wants consensus to commit */;
let digest = blake2s_to_felt(b"PRECOMMIT_VOTE" || target_block_hash.to_bytes_be());
let forged_sig = ecdsa_sign(&private_key, &digest).unwrap();
// Broadcast forged_sig as a precommit vote from any validator address.

# 4. Debug leak (secondary):
println!("{:?}", signature_manager);
// Prints: SignatureManager { keystore: LocalKeyStore { public_key: ...,
//         private_key: PrivateKey(0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133) } }
```

### Citations

**File:** crates/starknet_api/src/crypto/utils.rs (L42-45)
```rust
#[derive(
    Debug, Default, derive_more::Deref, Copy, Clone, Eq, PartialEq, Hash, Deserialize, Serialize,
)]
pub struct PrivateKey(pub Felt);
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L49-52)
```rust
#[derive(Clone, Debug)]
pub struct SignatureManager<KS: KeyStore> {
    pub keystore: KS,
}
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L68-82)
```rust
    pub async fn sign_precommit_vote(
        &self,
        block_hash: BlockHash,
    ) -> SignatureManagerResult<RawSignature> {
        let message_digest = build_precommit_vote_message_digest(block_hash);
        self.sign(message_digest).await
    }

    async fn sign(&self, message_digest: MessageDigest) -> SignatureManagerResult<RawSignature> {
        let private_key = self.keystore.get_key().await?;
        let signature = ecdsa_sign(&private_key, &message_digest)
            .map_err(|e| SignatureManagerError::Sign(e.to_string()))?;

        Ok(signature.into())
    }
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L89-93)
```rust
#[derive(Clone, Copy, Debug)]
pub struct LocalKeyStore {
    pub public_key: PublicKey,
    private_key: PrivateKey,
}
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L101-111)
```rust
    pub(crate) const fn new_for_testing() -> Self {
        // Created using `cairo-lang`.
        const PRIVATE_KEY: PrivateKey = PrivateKey(Felt::from_hex_unchecked(
            "0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133",
        ));
        const PUBLIC_KEY: PublicKey = PublicKey(Felt::from_hex_unchecked(
            "0x125d56b1fbba593f1dd215b7c55e384acd838cad549c4a2b9c6d32d264f4e2a",
        ));

        Self { private_key: PRIVATE_KEY, public_key: PUBLIC_KEY }
    }
```

**File:** crates/apollo_signature_manager/src/lib.rs (L41-43)
```rust
pub fn create_signature_manager() -> SignatureManager {
    SignatureManager::new()
}
```

**File:** crates/apollo_node/src/components.rs (L555-561)
```rust
    let signature_manager = match config.components.signature_manager.execution_mode {
        ReactiveComponentExecutionMode::LocalExecutionWithRemoteDisabled
        | ReactiveComponentExecutionMode::LocalExecutionWithRemoteEnabled => {
            Some(create_signature_manager())
        }
        ReactiveComponentExecutionMode::Disabled | ReactiveComponentExecutionMode::Remote => None,
    };
```
