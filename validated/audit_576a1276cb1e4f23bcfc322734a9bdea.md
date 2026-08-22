### No Vulnerability found for this question.

The premise conflates two unrelated things. `get_public_pem` in `src/secure_element.rs` is a `#[cfg(test)]`-only function that reads the mocked in-memory ECDSA signing key used only by unit tests; it has no reachable path in production builds (`cfg(not(test))`) and is never involved in choosing or validating the custody encryption target. [1](#0-0) 

Its only caller is the test module of `personal_custody_package.rs`, which uses it purely to dump the mock signing key to disk for the `test_generate_dummy_personal_custody_package_v3`/`v2` fixtures. [2](#0-1) [3](#0-2) 

Separately, the actual encryption target for the self-custody tiers is `self_custody_user_public_key` on the `Credentials` struct, which is unrelated to `get_public_pem`/`get_private_pem` and is sourced from `src/backend/user_status.rs` / `src/plans/mod.rs`, not from the secure-element signing key. [4](#0-3) 

Since `get_public_pem` is test-only code with no production reachability, and it is not the key used to encrypt custody data, there is no attacker-reachable path through this function per the rules excluding test-only/mock-only paths.

### Citations

**File:** src/secure_element.rs (L64-68)
```rust
#[cfg(test)]
pub fn get_public_pem() -> Result<String> {
    let pkey = SIGNING_KEY.lock().unwrap();
    Ok(String::from_utf8(pkey.public_key_to_pem()?)?)
}
```

**File:** src/plans/personal_custody_package.rs (L282-352)
```rust
impl Package<'_> {
    fn build(&self) -> Result<(Vec<u8>, Vec<u8>, Vec<u8>)> {
        let Self { ts, ref credentials, .. } = *self;
        let Credentials {
            backend_iris_public_key,
            backend_normalized_iris_public_key,
            backend_face_public_key,
            backend_tier2_public_key,
            self_custody_user_public_key,
            pcp_version,
            ..
        } = credentials;
        let mut hashes = BTreeMap::new();
        let mut tier0 = tar::Builder::new(Vec::new());
        let mut tier1 = tar::Builder::new(Vec::new());
        let mut tier2 = tar::Builder::new(Vec::new());

        let mut iris_tar = self.make_iris_tar(&mut hashes)?;
        iris_tar = encrypt(iris_tar, backend_iris_public_key);

        let mut normalized_iris_tar = self.make_normalized_iris_tar(&mut hashes)?;
        normalized_iris_tar = encrypt(normalized_iris_tar, backend_normalized_iris_public_key);

        let mut face_tar = self.make_face_tar(&mut hashes)?;
        face_tar = encrypt(face_tar, backend_face_public_key);

        let backend_keys_json = self.make_backend_keys_json(&mut hashes)?;

        if *pcp_version >= 3 {
            tar_append(&mut tier1, ts, "iris.tar", iris_tar)?;
            tar_append(&mut tier1, ts, "normalized_iris.tar", normalized_iris_tar)?;
            tar_append(&mut tier1, ts, "face.tar", face_tar)?;
            self.make_tier2(&mut tier2)?;
        } else {
            tar_append(&mut tier0, ts, "iris.tar", iris_tar)?;
            tar_append(&mut tier0, ts, "normalized_iris.tar", normalized_iris_tar)?;
            tar_append(&mut tier0, ts, "face.tar", face_tar)?;
        }

        let tier1_compressed = compress(tier1.into_inner()?, ts, "tier1.tar.gz")?;
        let tier1_encrypted = encrypt(tier1_compressed, self_custody_user_public_key);
        let tier2_compressed = compress(tier2.into_inner()?, ts, "tier2.tar.gz")?;
        let tier2_single_encrypted = backend_tier2_public_key
            .map(|backend_tier2_public_key| encrypt(tier2_compressed, &backend_tier2_public_key))
            .unwrap_or_default();
        let tier2_encrypted = encrypt(tier2_single_encrypted, self_custody_user_public_key);

        let info_json = self.make_info_json(&mut hashes)?;
        let face_embeddings_json = self.make_face_embeddings_json(&mut hashes)?;
        let iris_codes_json = self.make_iris_codes_json(&mut hashes)?;
        let iris_code_shares_jsons = self.make_iris_code_shares_jsons(&mut hashes)?;

        let hashes_json = self.make_hashes_json(
            hashes,
            digest(&SHA256, &tier1_encrypted),
            digest(&SHA256, &tier2_encrypted),
        )?;

        tar_append(&mut tier0, ts, "info.json", info_json)?;
        tar_append(&mut tier0, ts, "face_embeddings.json", face_embeddings_json)?;
        tar_append(&mut tier0, ts, "iris_codes.json", iris_codes_json)?;
        for (i, share_json) in iris_code_shares_jsons.iter().enumerate() {
            tar_append(&mut tier0, ts, &format!("iris_code_shares_{i}.json"), share_json)?;
        }
        tar_append(&mut tier0, ts, "hashes.sign", sign(digest(&SHA256, &hashes_json))?)?;
        tar_append(&mut tier0, ts, "hashes.json", hashes_json)?;
        tar_append(&mut tier0, ts, "backend_keys.json", backend_keys_json)?;

        let tier0_compressed = compress(tier0.into_inner()?, ts, "tier0.tar.gz")?;
        let tier0_encrypted = encrypt(tier0_compressed, self_custody_user_public_key);
        Ok((tier0_encrypted, tier1_encrypted, tier2_encrypted))
```

**File:** src/plans/personal_custody_package.rs (L804-811)
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        agents::camera::rgb,
        backend::operator_status::Coordinates,
        secure_element::{get_private_pem, get_public_pem},
    };
```

**File:** src/plans/personal_custody_package.rs (L986-989)
```rust
        fs::write(dir.join("orb_secure_element_private_secp256k1.pem"), get_private_pem().unwrap())
            .unwrap();
        fs::write(dir.join("orb_secure_element_public_secp256k1.pem"), get_public_pem().unwrap())
            .unwrap();
```
