No vulnerability found for this question.

**Rationale:**

`decryption_key_cloned` in `types/src/decryption.rs` is a trivial accessor that clones the `decryption_key` bytes stored inside `BlockTxnDecryptionKey`; it performs no lookup, insertion, or comparison against any cache and has no role in binding a key to `DecKeyMetadata` beyond the fact that both fields already live together in the same immutable struct instance. [1](#0-0) 

There is no "round-keyed cache" in `decryption_pipeline_builder.rs` that stores decryption keys indexed by `DecKeyMetadata` for later reuse across blocks. Each block computes its own key material fresh: the digest that the decryption key is derived against is a cryptographic function of the block's own `digest_round` (chained round or `block.round()`), and the resulting `SecretSharedKey`/`BlockTxnDecryptionKey` is produced per-block via `FPTXWeighted::digest`, `derive_decryption_key_share`, and the final decrypt call. [2](#0-1) 

Additionally, before applying a key to any ciphertext, the code explicitly checks that the transaction's `encryption_epoch` matches `decryption_key.metadata.epoch`, rejecting the transaction with `EpochMismatch` otherwise — this is the actual binding/guard the pipeline relies on, and it operates per-transaction, not via any mutable cache that could be poisoned by a "duplicated invocation" of a getter method. [3](#0-2) 

Because the digest (and therefore the derived decryption key) is cryptographically tied to the specific `digest_round`/epoch via `FPTXWeighted::digest`, simply reusing old raw key bytes for a different round would not successfully decrypt that round's ciphertexts — there is no code path where an old key's bytes are silently reassociated with a new `(epoch, round)` tuple to enable "premature disclosure." The premise of a "round-keyed cache" whose uniqueness invariant `decryption_key_cloned` could violate does not match the actual implementation.

This is also outside the review's custody scope: it concerns consensus-internal transaction-decryption plumbing, not an unprivileged Move entry point that reassigns ownership, mints/burns/freezes assets, or corrupts multisig/resource-account/object custody state.

### Citations

**File:** types/src/decryption.rs (L15-48)
```rust
#[derive(Clone, Serialize, Deserialize, Debug, Default, PartialEq, Eq)]
pub struct BlockTxnDecryptionKey {
    metadata: DecKeyMetadata,
    #[serde(with = "serde_bytes")]
    decryption_key: Vec<u8>,
}

impl BlockTxnDecryptionKey {
    pub fn new(metadata: DecKeyMetadata, decryption_key: Vec<u8>) -> Self {
        Self {
            metadata,
            decryption_key,
        }
    }

    pub fn metadata(&self) -> &DecKeyMetadata {
        &self.metadata
    }

    pub fn epoch(&self) -> u64 {
        self.metadata.epoch
    }

    pub fn round(&self) -> Round {
        self.metadata.round
    }

    pub fn decryption_key(&self) -> &[u8] {
        &self.decryption_key
    }

    pub fn decryption_key_cloned(&self) -> Vec<u8> {
        self.decryption_key.clone()
    }
```

**File:** consensus/src/pipeline/decryption_pipeline_builder.rs (L440-464)
```rust
    let digest_key = secret_share_config.digest_key_arc();
    let (txn_ciphertexts, digest, proofs_promise) = tokio::task::spawn_blocking(move || {
        monitor!(
            "decryption_digest",
            DIGEST_POOL.install(|| {
                FPTXWeighted::digest(&digest_key, &txn_ciphertexts, digest_round)
                    .map(|(digest, proofs_promise)| (txn_ciphertexts, digest, proofs_promise))
            })
        )
    })
    .await
    .map_err(|e| anyhow!("digest computation panicked: {e}"))??;

    let metadata = SecretShareMetadata::new(
        block.epoch(),
        block.round(),
        block.timestamp_usecs(),
        block.id(),
        digest.clone(),
    );

    let derived_key_share = monitor!(
        "decryption_derive_key_share",
        FPTXWeighted::derive_decryption_key_share(secret_share_config.msk_share(), &digest)?
    );
```

**File:** consensus/src/pipeline/decryption_pipeline_builder.rs (L580-599)
```rust
                let payload_encryption_epoch = txn
                    .payload()
                    .as_encrypted_payload()
                    .expect("must happen")
                    .encryption_epoch();

                if payload_encryption_epoch != decryption_key.metadata.epoch {
                    warn!(
                        "transaction with ciphertext id {:?} has encryption epoch {} but decryption key epoch {}",
                        id,
                        payload_encryption_epoch,
                        decryption_key.metadata.epoch,
                    );
                    num_failed_decryptions.fetch_add(1, Ordering::Relaxed);
                    return mark_txn_failed_decryption(
                        txn,
                        Some(eval_proof),
                        DecryptionFailureReason::EpochMismatch,
                    );
                }
```
