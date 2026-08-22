### Title
Stale, un-refreshable `ORB_PUBLIC_KEY` cached for process lifetime is embedded as the attestation certificate in every signup's Personal Custody Package - (File: `src/identification.rs`)

### Summary
`ORB_PUBLIC_KEY` is read once from the secure-element keystore file and cached for the entire process lifetime via a `once_cell::sync::Lazy` static, with no setter or refresh mechanism analogous to the `exchangeRateFeeder` issue in the referenced report. This cached value is embedded verbatim as the `orb_public_key_certificate` in the `InfoJson` attestation metadata written into every signup's Personal Custody Package (PCP), so if the underlying key ever changes without a full process restart, every subsequent signup in that process's lifetime would be attested with a stale/incorrect public key.

### Finding Description
`ORB_PUBLIC_KEY` is defined as a lazily-initialized, immutable static that reads the secure-element keystore file exactly once, on first access, and caches the result for the lifetime of the `orb-core` process: [1](#0-0) 

There is no setter, invalidation hook, or periodic re-read for this value anywhere in `src/identification.rs` — unlike `ORB_TOKEN`, which is explicitly designed with a mutable `Arc<RwLock<...>>` so it can be refreshed at runtime: [2](#0-1) 

This cached, unrefreshable key is then used, per signup, to populate `orb_public_key_certificate` in the info manifest that is packaged as part of the PCP and uploaded as part of the signup's cryptographic attestation trail: [3](#0-2) [4](#0-3) 

This is structurally the same bug class as the reported `exchangeRateFeeder` issue: an externally-sourced value that documentation/design assumes "may change" is fetched once and cached indefinitely with no setter, and that stale value is then used as an authoritative input into every subsequent critical operation (there: share/asset calculations; here: the signup's identity/attestation certificate) for as long as the process runs.

### Impact Explanation
If the secure-element public key is rotated or re-provisioned (e.g., due to key rotation, repair, or re-manufacturing flows) while the `orb-core` process keeps running (i.e., without a full process restart that would re-run the `Lazy` initializer), every signup processed after that point would have its PCP `info.json` stamped with the old, now-incorrect `orb_public_key_certificate`. This causes attestation forgery/misattribution: the cryptographic identity certificate bound into the signup's custody package no longer matches the orb's actual current key, undermining downstream verification of which orb/key produced a given signup's PCP, and could allow a signup's provenance to be misattributed to a stale identity.

### Likelihood Explanation
Likelihood is moderate-to-low because it requires the key material at `ORB_PUBLIC_KEY_PATH` to change while the `orb-core` process is still alive (no code path in the reviewed files performs in-process key rotation), so a coincident service restart is normally expected. However, `orb-core` is a long-running daemon and nothing in the codebase enforces that a key change is always paired with a process restart before the next signup — the caching mechanism itself provides no safety net, exactly mirroring the "async model" caveat noted in the original report where the incorrect value keeps being used until an external event (redeploy/restart) fixes it.

### Recommendation
Do not treat `ORB_PUBLIC_KEY` as a permanently cached process-lifetime constant. Re-read the keystore file (or provide an explicit setter/invalidation function) each time the value is needed for a signup-critical operation such as building `InfoJson`, or at minimum re-validate it against the on-disk value before embedding it into a PCP, so key rotation is reflected without requiring a coincidental process restart.

### Proof of Concept
1. Start `orb-core`; on first access, `ORB_PUBLIC_KEY` is lazily read from `/usr/persistent/se/keystore/sss_70000002_0002_0040.bin` and cached in memory (`src/identification.rs:65-68`).
2. Perform a signup — `personal_custody_package::Plan::make_info_json` embeds the cached value as `orb_public_key_certificate` (`src/plans/personal_custody_package.rs:478`).
3. Rotate/replace the key file on disk (simulating a key-rotation/repair event) without restarting the `orb-core` process.
4. Perform another signup in the same running process — the newly generated PCP `info.json` still contains the old, now-stale `orb_public_key_certificate`, because `Lazy` never re-reads the file, and there is no setter to force a refresh.

### Citations

**File:** src/identification.rs (L42-44)
```rust
/// Orb token.
pub static ORB_TOKEN: Lazy<Arc<RwLock<result::Result<String, TokenError>>>> =
    Lazy::new(|| Arc::new(RwLock::new(Err(TokenError::NotRequested()))));
```

**File:** src/identification.rs (L65-68)
```rust
/// The Orb's public key.
#[cfg(not(test))]
pub static ORB_PUBLIC_KEY: Lazy<Vec<u8>> =
    Lazy::new(|| fs::read(ORB_PUBLIC_KEY_PATH).expect("couldn't read orb public key"));
```

**File:** src/plans/personal_custody_package.rs (L471-478)
```rust
        let orb_id = ORB_ID.as_str();
        let timestamp = self
            .capture_start
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
            .to_string();
        let orb_public_key_certificate = BASE64.encode(&ORB_PUBLIC_KEY);
```

**File:** src/plans/personal_custody_package.rs (L505-526)
```rust
        let info = InfoJson {
            signup_id,
            signup_id_salt,
            signup_reason,
            signup_reason_salt,
            orb_id,
            orb_id_salt,
            operator_id: &operator_qr_code.user_id,
            operator_id_salt,
            timestamp,
            timestamp_salt,
            qr_code: user_qr_code_string,
            qr_code_salt,
            orb_public_key_certificate,
            left_ir_image_id,
            right_ir_image_id,
            thumbnail_image_id,
            software_version,
            software_version_salt,
            orb_country,
            orb_country_salt,
        };
```
