### Title
Disk Rollback by Untrusted Host Enables Presignature Reuse and ECDSA Private Key Recovery - (File: `crates/node/src/assets.rs`)

### Summary

The MPC node deletes presignatures from its RocksDB store after consumption via `DistributedAssetStorage::take_owned()`, but there is no anti-rollback mechanism protecting the database. The host OS — explicitly modeled as untrusted with full root access — can replace the disk with an old snapshot, restoring consumed presignatures. An attacker controlling the host OS of all nodes that participated in a presigning can cause presignature reuse, enabling ECDSA nonce-reuse attacks and full private key recovery. This is an acknowledged open risk in the project's own threat model with no current mitigation.

### Finding Description

`DistributedAssetStorage::take_owned()` atomically removes a presignature from RocksDB and returns it for use in signing: [1](#0-0) 

The underlying `SecretDB` encrypts values with AES-128-GCM: [2](#0-1) 

However, AES-GCM encryption only protects against unauthorized reads of the ciphertext. It does not prevent the host OS from replacing the entire encrypted RocksDB directory with an older snapshot. After a rollback, the node decrypts and uses the restored data as if it were current, because the same Gramine-sealed disk encryption key (derived from CVM measurements) decrypts both the current and the rolled-back snapshot identically.

The project's own threat model explicitly classifies this as an open risk with no current mitigation: [3](#0-2) [4](#0-3) 

The host OS capabilities listed in the threat model diagram explicitly include "Replace disk snapshots": [5](#0-4) 

The cryptographic security documentation for both ECDSA variants is unambiguous about the consequence of presignature reuse: [6](#0-5) [7](#0-6) 

The OT-based ECDSA orchestration documentation similarly states that consumed outputs must be destroyed and that reuse is catastrophic: [8](#0-7) 

The `DistributedAssetStorage` stores presignatures in `DBCol::Presignature` and triples in `DBCol::TripleV2`, both inside the same RocksDB instance: [9](#0-8) 

There is no monotonic counter, sequence number, or write-once consumed-ID log anywhere in the storage layer that would survive a disk rollback and prevent the node from treating restored presignatures as fresh.

### Impact Explanation

Presignature reuse produces two ECDSA signatures over different messages using the same ephemeral nonce (the same `R` value). This is the classical ECDSA nonce-reuse condition: given signatures `(R, s1)` over `h1` and `(R, s2)` over `h2`, the private key `x` is recoverable in closed form. Because the MPC network's private key is the secret being protected, recovering it grants the ability to sign arbitrary transactions for any address derived from that key — enabling theft of all funds controlled by the MPC network across every supported chain (Ethereum, Bitcoin, Solana, etc.).

### Likelihood Explanation

The threat model explicitly assumes the host OS is adversarial with full root access and lists disk snapshot replacement as a host capability. An attacker who controls the hosting infrastructure for all nodes that participated in a given presigning session (e.g., a cloud provider, a co-located data-center operator, or a nation-state actor with access to the hosting provider) can execute this attack. The presigning participant set is a subset of the full network (determined by which nodes are online), so the attacker does not need to control all nodes — only those that participated in the specific presigning. Signatures are submitted publicly to the NEAR contract, so the attacker can observe both signatures on-chain without any additional access.

### Recommendation

Implement an anti-rollback mechanism for the presignature and triple stores. Concrete options:

1. **TEE monotonic counter**: Use Intel TDX's or SGX's hardware monotonic counter to record the last consumed presignature sequence number. The counter cannot be decremented by the host OS. Before consuming a presignature, verify the counter matches the expected value.
2. **Remote attestation freshness check**: Before each signing session, require a fresh remote attestation quote that binds the current database state hash. A rolled-back database would produce a different hash, detectable by peers.
3. **Peer-witnessed consumed-ID log**: Broadcast consumed presignature IDs to peer nodes over the mTLS mesh. Peers refuse to participate in signing with a presignature ID they have already seen consumed, even if the leader presents it again.

### Proof of Concept

1. Attacker controls the host OS of all nodes that participated in presigning presignature `P1` (e.g., nodes A, B, C in a 3-of-5 network).
2. Attacker takes a filesystem snapshot of the RocksDB `assets/` directory on each of A, B, C.
3. The MPC network uses `P1` to sign message `M1`; `take_owned()` deletes `P1` from A's DB; `take_unowned()` deletes `P1`'s follower shares from B and C's DBs. Signature `S1 = (R, s1)` is submitted on-chain.
4. Attacker restores the RocksDB snapshot on A, B, and C simultaneously. `P1` reappears in all three databases.
5. Attacker submits a new signing request for message `M2` to the NEAR contract. The leader (A) calls `take_owned()`, retrieves `P1` again, and initiates signing. B and C call `take_unowned(P1_id)`, find it in their restored databases, and participate. Signature `S2 = (R, s2)` is submitted on-chain.
6. Attacker reads `S1` and `S2` from the NEAR contract. Both share the same `R` (same presignature nonce). Using the standard relation `x = (s1·h2 - s2·h1) / (s2 - s1) · R_x^{-1}` (mod q), the attacker recovers the MPC network's private key `x`.
7. Attacker uses `x` to sign arbitrary withdrawal transactions, draining all funds.

### Citations

**File:** crates/node/src/assets.rs (L497-504)
```rust
    pub async fn take_owned(&self) -> (UniqueId, T) {
        let (id, asset) = self.owned_queue.take_owned().await;
        let mut update = self.db.update();
        update.delete(self.col, &self.make_key(id));
        update
            .commit()
            .expect("Unrecoverable error writing to database");
        (id, asset)
```

**File:** crates/node/src/db.rs (L11-16)
```rust
/// Key-value store that encrypts all values with AES-GCM.
/// The keys of the key-value store are NOT encrypted.
pub struct SecretDB {
    db: rocksdb::DB,
    cipher: Aes128Gcm,
}
```

**File:** crates/node/src/db.rs (L26-36)
```rust
pub enum DBCol {
    /// Per-`t` triple column: keys are `[t as u64 BE][borsh(UniqueId)]`. A
    /// triple is stored under the threshold it was generated with so that
    /// presign can draw from a store of matching `t`.
    TripleV2,
    Presignature,
    SignRequest,
    CKDRequest,
    VerifyForeignTxRequest,
    EpochData,
}
```

**File:** docs/threat-model-diagram.md (L44-47)
```markdown
    subgraph HOST["Host OS"]
        direction TB
        HOST_CAP["Host Capabilities:<br/>- Read/modify env vars<br/>- Observe logs<br/>- Intercept local traffic<br/>- Attempt pubkey substitution<br/>- Replace disk snapshots"]

```

**File:** docs/threat-model-diagram.md (L281-281)
```markdown
| T6 | Rollback / replay attack | Replace disk with old snapshot | Host OS -> Encrypted Disk | **Open risk** — triples/presigs could be reused | Future mitigation needed |
```

**File:** docs/securing-mpc-with-tee-design-doc.md (L865-867)
```markdown
- **Rollback & asset reuse**
  - An entire MPC node disk may be replaced with a previous snapshot, leading to reuse of cryptographic assets (e.g., triples, presignatures).
  - Currently, these assets are persisted on disk — mitigation will be required in future iterations.
```

**File:** crates/threshold-signatures/docs/ecdsa/robust_ecdsa/signing.md (L150-158)
```markdown
be aware that it is vulnerable to **split-view attacks** in the robust setting when the
signing parameters are not globally consistent. If different subsets of size at least
$2t + 1$ sign different $(h, \epsilon)$ values using shares derived from the same
presignature, the resulting signatures use multiplicatively related nonces and the
secret key can be recovered using standard ECDSA nonce-reuse attacks.

Moreover, due to protocol modifications relative to [[DJNPO20](https://eprint.iacr.org/2020/501)] (notably signature-share
linearization), **a novel split-view attack exists that can extract the secret key using as
few as $2t + 2$ presigning participants**, with as few as two signing sessions.
```

**File:** crates/threshold-signatures/docs/ecdsa/robust_ecdsa/signing.md (L176-177)
```markdown
3. **Never reuse a presignature**, even across failed, aborted, or partially completed
   signing sessions.
```

**File:** crates/threshold-signatures/docs/ecdsa/ot_based_ecdsa/orchestration.md (L64-79)
```markdown
## Discarding information

Each phase can be run many times in advance, recording the information
public information produced, as well as the list of parties which produced it.
Then, this output is consumed by having a set of parties use it
for a subsequent phase.
It's **critical** that the output is then destroyed, so that no other
group of parties attempts to re-use that output for another phase.
In particular, the parties need some way of agreeing on which
outputs have been created and used.
If the threshold $t_i$ is such that $N_{i} \leq 2t - 1$, then it's impossible
to have two non-overlapping quorums, so if each party locally registers the
fact that an output has been used, then agreement can be had not to
use a certain output.
Otherwise, you might have two independent groups of parties trying
to use the same output, which is bad.
```
