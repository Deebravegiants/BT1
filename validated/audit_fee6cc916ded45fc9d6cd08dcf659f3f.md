### Title
Consensus Signing Private Key Stored as Plaintext in Memory; Production `create_signature_manager()` Hardcodes a Publicly Known Test Key — (File: `crates/apollo_signature_manager/src/lib.rs`, `crates/apollo_signature_manager/src/signature_manager.rs`)

---

### Summary

The `LocalKeyStore` struct stores the consensus node's ECDSA private key as a plain `PrivateKey` (`Felt`) in memory with no memory protection and no zeroing on drop. More critically, the production entry-point `create_signature_manager()` — called from `crates/apollo_node/src/components.rs` — unconditionally instantiates `LocalKeyStore::new_for_testing()`, which hardcodes the private key `0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133` (publicly visible in the repository). This key is used to sign every precommit vote the node broadcasts to the consensus network.

---

### Finding Description

**Plaintext key in memory (`LocalKeyStore`):**

`LocalKeyStore` is declared as:

```rust
#[derive(Clone, Copy, Debug)]
pub struct LocalKeyStore {
    pub public_key: PublicKey,
    private_key: PrivateKey,   // plain Felt, no zeroize, no secrecy wrapper
}
``` [1](#0-0) 

The `Debug` derive means the private key can appear in any log line that formats the `SignatureManager` or its `keystore` field (which is `pub`). There is no `Drop` implementation to zero the key bytes, so the key persists in heap/stack memory for the lifetime of the process. [2](#0-1) 

**Hardcoded test key shipped to production:**

`LocalKeyStore::new_for_testing()` embeds a fixed, source-visible private key:

```rust
pub(crate) const fn new_for_testing() -> Self {
    const PRIVATE_KEY: PrivateKey = PrivateKey(Felt::from_hex_unchecked(
        "0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133",
    ));
    ...
}
``` [3](#0-2) 

The production type alias and factory function both resolve to this key:

```rust
pub type SignatureManager = LocalKeyStoreSignatureManager;

// TODO(Elin): understand how key store would look in production ...
pub fn create_signature_manager() -> SignatureManager {
    SignatureManager::new()   // → LocalKeyStore::new_for_testing()
}
``` [4](#0-3) 

`create_signature_manager()` is called from the production node component wiring in `crates/apollo_node/src/components.rs`.

**Signing path that uses this key:**

The `SignatureManager` signs every precommit vote the node emits:

```rust
async fn sign(&self, message_digest: MessageDigest) -> SignatureManagerResult<RawSignature> {
    let private_key = self.keystore.get_key().await?;
    let signature = ecdsa_sign(&private_key, &message_digest)...;
    Ok(signature.into())
}
``` [5](#0-4) 

The `SignatureManagerRequest::SignPrecommitVote` handler routes directly to `sign_precommit_vote(block_hash)`: [6](#0-5) 

---

### Impact Explanation

Every sequencer node running this code signs its precommit votes with the same publicly known private key. An adversary who reads the repository can:

1. Derive the corresponding public key `0x125d56b1fbba593f1dd215b7c55e384acd838cad549c4a2b9c6d32d264f4e2a`.
2. Forge valid ECDSA precommit-vote signatures over any `BlockHash` they choose.
3. Inject those forged votes into the consensus network, impersonating any validator that uses this build.

If signature verification is enforced (the `verify_precommit_vote_signature` library function exists for exactly this purpose), a single attacker with network access can cast a quorum of forged precommit votes for a block of their choosing, causing the consensus layer to decide on a wrong block. This maps directly to the allowed impact: **"Transaction conversion or signature/hash logic binds the wrong signer."**

Even if signature verification is not yet enforced end-to-end, the plaintext in-memory storage means any memory-read primitive (process dump, core file, debug interface) exposes the key — the direct analog of the external report's Redux-store disclosure.

---

### Likelihood Explanation

- The private key is embedded in source code and visible to anyone with repository access.
- The production factory `create_signature_manager()` contains a `TODO` acknowledging the key is a placeholder, confirming this is not an intentional design choice.
- No configuration path exists to supply a real key; the only implementation of `KeyStore` is `LocalKeyStore`.
- The `Debug` derive on `LocalKeyStore` means the key can leak into structured logs at any `debug!` or `error!` call site that formats the manager.

---

### Recommendation

**Short term:**
- Remove `LocalKeyStore::new_for_testing()` from the production `create_signature_manager()` path immediately.
- Load the private key from an operator-supplied secret (environment variable, mounted Kubernetes secret, or HSM) and wrap it in a `secrecy::Secret<[u8; 32]>` (the same pattern already used for `NetworkConfig::secret_key`). [7](#0-6) 

- Add `#[cfg(test)]` to `new_for_testing()` so it cannot be called from non-test code.

**Long term:**
- Implement a `KeyStore` backed by an HSM or remote signing service so the raw private key bytes never reside in process memory.
- Add `zeroize::Zeroize` / `zeroize::ZeroizeOnDrop` to any struct that holds a private key.
- Remove the `Debug` derive from `LocalKeyStore` (or implement it manually to redact the key).

---

### Proof of Concept

```
# 1. Extract the hardcoded private key from the source:
grep -r "608bf2cdb1ad4138" crates/
# → crates/apollo_signature_manager/src/signature_manager.rs

# 2. Derive the public key (matches the hardcoded PUBLIC_KEY constant):
#    public_key = get_public_key(0x608bf2cdb1ad4138e72d2f82b8c5db9fa182d1883868ae582ed373429b7a133)
#    = 0x125d56b1fbba593f1dd215b7c55e384acd838cad549c4a2b9c6d32d264f4e2a

# 3. For any target block_hash H, compute:
#    message = b"PRECOMMIT_VOTE" || H.to_bytes_be()
#    digest  = blake2s_to_felt(message)
#    (r, s)  = ecdsa_sign(private_key=0x608bf2..., message=digest)

# 4. Broadcast a Vote{vote_type: Precommit, proposal_commitment: H,
#    voter: <any validator address>, signature: (r,s)}
#    to the consensus P2P topic.

# Because every honest node also signs with the same key, the forged
# signature is indistinguishable from a legitimate one.
``` [8](#0-7) [3](#0-2) [9](#0-8)

### Citations

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L49-52)
```rust
#[derive(Clone, Debug)]
pub struct SignatureManager<KS: KeyStore> {
    pub keystore: KS,
}
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L76-82)
```rust
    async fn sign(&self, message_digest: MessageDigest) -> SignatureManagerResult<RawSignature> {
        let private_key = self.keystore.get_key().await?;
        let signature = ecdsa_sign(&private_key, &message_digest)
            .map_err(|e| SignatureManagerError::Sign(e.to_string()))?;

        Ok(signature.into())
    }
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L88-93)
```rust
/// A simple in-memory key store.
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

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L138-145)
```rust
fn build_precommit_vote_message_digest(block_hash: BlockHash) -> MessageDigest {
    let block_hash = block_hash.to_bytes_be();
    let mut message = Vec::with_capacity(PRECOMMIT_VOTE.len() + block_hash.len());
    message.extend_from_slice(PRECOMMIT_VOTE);
    message.extend_from_slice(&block_hash);

    MessageDigest(blake2s_to_felt(&message))
}
```

**File:** crates/apollo_signature_manager/src/lib.rs (L14-43)
```rust
#[derive(Clone, Debug)]
pub struct LocalKeyStoreSignatureManager(pub GenericSignatureManager<LocalKeyStore>);

impl LocalKeyStoreSignatureManager {
    pub fn new() -> Self {
        Self(GenericSignatureManager::new(LocalKeyStore::new_for_testing()))
    }
}

impl Default for LocalKeyStoreSignatureManager {
    fn default() -> Self {
        Self::new()
    }
}

impl Deref for LocalKeyStoreSignatureManager {
    type Target = GenericSignatureManager<LocalKeyStore>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

pub use LocalKeyStoreSignatureManager as SignatureManager;

// TODO(Elin): understand how key store would look in production and better define the way the
// signature manager is created.
pub fn create_signature_manager() -> SignatureManager {
    SignatureManager::new()
}
```

**File:** crates/apollo_signature_manager/src/communication.rs (L30-34)
```rust
            SignatureManagerRequest::SignPrecommitVote(block_hash) => {
                SignatureManagerResponse::SignPrecommitVote(
                    self.sign_precommit_vote(block_hash).await,
                )
            }
```

**File:** crates/apollo_network/src/lib.rs (L413-420)
```rust
                "secret_key",
                &serialize_optional_vec_u8(
                    &self.secret_key.as_ref().map(|s| s.clone().expose_secret()),
                ),
                "The secret key used for building the peer id. If it's an empty string a random one \
                 will be used.",
                ParamPrivacyInput::Private,
            ),
```
