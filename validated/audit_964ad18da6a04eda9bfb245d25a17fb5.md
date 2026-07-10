### Title
Plaintext Storage of Cryptographic Secrets (P2P Key + AES Keyshare Key) in `backup-cli` `secrets.json` Without File Permission Restrictions — (File: `crates/backup-cli/src/adapters/secrets_storage.rs`)

---

### Summary

The `backup-cli` tool writes its `PersistentSecrets` — which contains the Ed25519 P2P private key (used for mutual-TLS authentication to MPC nodes' migration endpoints), the NEAR signer key, and the AES-128 key used to encrypt locally stored keyshares — to a plain JSON file (`secrets.json`) with no encryption and no restrictive file permissions. The MPC node itself uses a dedicated `write_secret_file` helper that enforces `0o600` permissions; the backup-cli does not. An attacker with read access to the backup-cli home directory obtains all three secrets in cleartext, enabling them to decrypt any locally stored keyshares and to impersonate the registered backup service against MPC nodes.

---

### Finding Description

`JsonSecretsStorage::store_secrets()` serializes `PersistentSecrets` with `serde_json::to_vec` and writes the result directly to disk: [1](#0-0) 

The file is opened with: [2](#0-1) 

No `.mode(0o600)` call is made. The file is created with the process's default umask (typically `0o644` or `0o664`), making it potentially world-readable.

The struct written to this file is: [3](#0-2) 

It contains:
- `p2p_private_key` — the Ed25519 key used for mutual-TLS authentication to MPC nodes' migration endpoints
- `near_signer_key` — the Ed25519 key for signing NEAR transactions as the backup service
- `local_storage_aes_key` — the AES-128 key used by `LocalPermanentKeyStorageBackend` to encrypt/decrypt keyshares stored locally [4](#0-3) 

By contrast, the MPC node's own `secrets.json` is written with explicit `0o600` permissions: [5](#0-4) 

The backup-cli's `gen_secrets_and_write_to_disk` equivalent (`store_secrets`) has no such protection.

---

### Impact Explanation

**Keyshare decryption**: The `local_storage_aes_key` in `secrets.json` is the exact key passed to `LocalPermanentKeyStorageBackend` to decrypt keyshares stored in the backup-cli's home directory: [6](#0-5) 

If the backup-cli has already performed a backup (i.e., keyshare files exist on disk), an attacker who reads `secrets.json` can immediately decrypt those keyshare files. The encryption key and the ciphertext it protects reside in the same directory, defeating the purpose of at-rest encryption.

**Backup-service impersonation**: The `p2p_private_key` is used for mutual-TLS authentication to the MPC node's migration endpoint (port 8079). Once the backup service is registered with the MPC contract, any holder of this private key can authenticate as the registered backup service and request keyshares from MPC nodes: [7](#0-6) 

Collecting threshold-many keyshares across nodes enables full private-key reconstruction, which constitutes unauthorized access to MPC key shares and materially enables forgery.

---

### Likelihood Explanation

The backup-cli is an operator-run tool, typically executed on a server or workstation. Because `secrets.json` is created without `0o600` permissions, it may be readable by other local users or processes on a shared host. Backups, snapshots, or log-collection agents that archive the home directory would also capture the file in cleartext. The documentation itself warns: *"Keep the `secrets.json` file secure. Anyone with access to this file can authenticate as your backup service and decrypt any keyshares stored locally"* — but the code provides no enforcement of this requirement. [2](#0-1) 

---

### Recommendation

1. **Short term**: Apply `0o600` permissions when creating `secrets.json` in the backup-cli, mirroring the pattern already used by the MPC node's `write_secret_file`.
2. **Long term**: Encrypt `PersistentSecrets` at rest using a passphrase or OS-level secret store (e.g., Linux keyring, macOS Keychain) before writing to disk, so that the AES keyshare encryption key is never stored in cleartext alongside the keyshares it protects.

---

### Proof of Concept

1. Operator runs `backup-cli --home-dir /backup generate-keys`, producing `/backup/secrets.json` with default permissions (e.g., `0o644`).
2. Operator runs `backup-cli get-keyshares ...`, storing encrypted keyshares under `/backup/permanent_keys/`.
3. Attacker with read access to `/backup/` reads `secrets.json`:
   ```json
   {
     "p2p_private_key": "ed25519:<base58-encoded-private-key>",
     "near_signer_key": "ed25519:<base58-encoded-private-key>",
     "local_storage_aes_key": [<16 plaintext bytes>]
   }
   ```
4. Attacker extracts `local_storage_aes_key` and passes it to `LocalPermanentKeyStorageBackend::load()` to decrypt the keyshare files in `/backup/permanent_keys/`, recovering the node's MPC keyshare in plaintext.
5. Attacker uses `p2p_private_key` to authenticate to additional MPC nodes' migration endpoints (port 8079) as the registered backup service, collecting further keyshares until threshold is reached. [1](#0-0) [3](#0-2) [8](#0-7)

### Citations

**File:** crates/backup-cli/src/adapters/secrets_storage.rs (L54-66)
```rust
impl JsonSecretsStorage<File> {
    pub async fn open_write(storage_path: impl AsRef<Path>) -> Result<Self, Error> {
        let file_path = storage_path.as_ref().join(SECRETS_FILE_NAME);
        let destination = File::options()
            .create(true)
            .truncate(true)
            .write(true)
            .open(file_path)
            .await
            .map_err(Error::OpenFile)?;

        Ok(Self { destination })
    }
```

**File:** crates/backup-cli/src/adapters/secrets_storage.rs (L80-93)
```rust
    pub async fn store_secrets(&mut self, secrets: &types::PersistentSecrets) -> Result<(), Error> {
        let encoded_secrets = serde_json::to_vec(&secrets).map_err(Error::JsonSerialization)?;

        self.destination
            .seek(std::io::SeekFrom::Start(0))
            .await
            .map_err(Error::SeekFromStart)?;
        self.destination
            .write_all(&encoded_secrets)
            .await
            .map_err(Error::Write)?;

        Ok(())
    }
```

**File:** crates/backup-cli/src/types.rs (L5-13)
```rust
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct PersistentSecrets {
    /// Ed25519 private key used for encrypting P2P communication with MPC nodes
    pub p2p_private_key: SigningKey,
    /// Ed25519 private key used for signing NEAR transactions
    pub near_signer_key: SigningKey,
    /// AES-128 key for encrypting locally stored keyshares
    pub local_storage_aes_key: [u8; 16],
}
```

**File:** crates/backup-cli/src/adapters/keyshare_storage.rs (L17-23)
```rust
impl KeyshareStorageAdapter {
    pub async fn new(home_dir: PathBuf, encryption_key: [u8; 16]) -> anyhow::Result<Self> {
        let backend = LocalPermanentKeyStorageBackend::new(home_dir, encryption_key).await?;
        let storage = PermanentKeyStorage::new(Box::new(backend)).await?;

        Ok(Self { storage })
    }
```

**File:** crates/node/src/config.rs (L192-208)
```rust
fn write_secret_file(path: &Path, data: &[u8]) -> anyhow::Result<()> {
    let mut file = fs::OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .mode(0o600)
        .open(path)
        .with_context(|| format!("failed to create secret file {}", path.display()))?;
    file.write_all(data)
        .with_context(|| format!("failed to write secret file {}", path.display()))?;
    fs::set_permissions(path, fs::Permissions::from_mode(0o600)).with_context(|| {
        format!(
            "failed to set permissions on secret file {}",
            path.display()
        )
    })?;
    Ok(())
```

**File:** crates/backup-cli/src/backup.rs (L61-66)
```rust
            let mpc_p2p_client = adapters::p2p_client::MpcP2PClient::new(
                subcommand_args.mpc_node_address,
                mpc_node_p2p_key,
                secrets.p2p_private_key,
                backup_encryption_key,
            );
```

**File:** crates/backup-cli/src/backup.rs (L68-73)
```rust
            let key_shares_storage = adapters::keyshare_storage::KeyshareStorageAdapter::new(
                home_dir.clone(),
                secrets.local_storage_aes_key,
            )
            .await
            .expect("failed to create keyshare storage");
```

**File:** crates/node/src/keyshare/local.rs (L30-41)
```rust
    async fn load(&self) -> anyhow::Result<Option<Vec<u8>>> {
        let keyfile = permanent_key_link(&self.home_dir);
        if !keyfile.exists() {
            return Ok(None);
        }
        let data = tokio::fs::read(&keyfile)
            .await
            .context("Failed to read key file")?;
        let cipher = Aes128Gcm::new(&self.encryption_key.into());
        let decrypted = db::decrypt(&cipher, &data).context("Failed to decrypt key file")?;
        Ok(Some(decrypted))
    }
```
