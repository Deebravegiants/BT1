I have enough evidence to establish the analog now.

### Title
Unauthenticated legacy QR-code format allows an unprivileged bystander to initiate a signup under another person's `user_id`, causing backend-side signup/state contention for the legitimate identity - (File: `src/plans/qr_scan/user.rs`, `src/backend/user_status.rs`)

### Summary
The reported bug lets anyone holding a trivial amount of a token permanently claim `RJLaunchEvent` slot keyed by `_token`, blocking the rightful issuer, because the contract performs no authorization check before consuming a globally-unique identifier. The orb-core analog is the legacy user-QR parsing path, where the `user_id` "slot" that is submitted to the signup backend can be populated from a plaintext, unsigned QR string that anyone can fabricate if they know or observe a victim's UUID, with no cryptographic binding enforced before the signup flow proceeds.

### Finding Description
`qr_scan::user::Data::try_parse` accepts two formats for the user QR code: a modern, hash-bound format via `decode_qr(code)` that populates `user_data_hash`, and a legacy plaintext format matched by `QR_CODE_V2` (`userid:<uuid>:<data_policy>`) that sets `user_data_hash: None`. [1](#0-0) 

When the orb validates this QR code with the backend, `backend::user_status::request` only performs the cryptographic `user_data.verify(user_data_hash)` check when the backend actually returns `authenticated_app_data` **and** the QR carried a `user_data_hash`. If the QR is in the legacy format (`user_data_hash` is `None`), the code takes the "old QR-code format" branch and skips identity verification entirely, trusting the plaintext `user_id` as-is. [2](#0-1) [3](#0-2) 

The unauthenticated `user_id` string is then forwarded directly into the signup submission (`distributorId`/`userId` form fields) and into the signup polling flow, without the orb ever confirming that the physical person in front of the camera is the actual owner of that `user_id`. [4](#0-3) 

Just as `createRJLaunchEvent()` required only proof of holding 1 Wei of `_token` (not proof of authorship/ownership) to occupy the unique `getRJLaunchEvent[_token]` slot, here an unprivileged bystander needs only to know/observe a target's plaintext `user_id` (e.g. by photographing/parsing a previously displayed legacy QR code, since it's unsigned and not bound to any secret) to construct a fabricated legacy QR string and drive a real signup attempt under that identity — with no proof of biometric or cryptographic ownership required beyond what the orb itself checks, which is nothing for this path.

### Impact Explanation
A malicious actor presenting a forged legacy-format QR code to an orb can trigger a signup transaction tagged with someone else's `user_id`, consuming that identity slot on the backend (e.g., marking it in-flight, duplicate, or fraud-flagged) exactly like squatting on `getRJLaunchEvent[_token]`. This can block or corrupt the legitimate user's own signup attempt when their identity has already been "used" by the imposter, and it misattributes the biometric capture (of the attacker, not the QR's rightful owner) toward the victim's `user_id` on the backend side — a direct analog to the "unauthorized/misattributed signup" impact class.

### Likelihood Explanation
The `QR_CODE_V2` legacy path is unconditionally compiled and reachable in `try_parse` (not gated behind a test-only or internal-data-acquisition feature), so any orb still accepting this format will process such QR codes. The only requirement to exploit it is knowledge of a target `user_id` string — a UUID that itself carries no secrecy guarantee once observed/leaked, in the same way `_token` ownership required only 1 Wei.

### Recommendation
Reject the legacy unauthenticated QR format in production (or require the backend to always return signed `authenticated_app_data` and enforce `user_data.verify(user_data_hash)` unconditionally), so that no signup can proceed for a `user_id` without cryptographic proof that the presented QR code was issued to and bound to that identity, mirroring the recommendation to gate `createRJLaunchEvent()` behind an authorization check rather than trusting unauthenticated possession.

### Proof of Concept
1. Attacker observes/derives a victim's plaintext `user_id` (UUID) from a previously used legacy-format QR code (`userid:<uuid>:<data_policy>`), which carries no `user_data_hash`. [5](#0-4) 
2. Attacker generates their own QR code image encoding `userid:<victim-uuid>:<policy>` and presents it to any orb during their own biometric capture session.
3. `try_parse` accepts it via the `QR_CODE_V2` branch, setting `user_data_hash: None`.
4. `backend::user_status::request` takes the "old QR-code format" branch, skipping `verify()`, and returns valid `UserData` for the victim's `user_id`. [6](#0-5) 
5. The signup proceeds and is submitted to the backend tagged with the victim's `user_id`, occupying/contending for that identity slot exactly as an attacker occupying `getRJLaunchEvent[_token]` blocks the rightful token issuer. [4](#0-3)

### Citations

**File:** src/plans/qr_scan/user.rs (L101-140)
```rust
impl Schema for Data {
    fn ui() -> ui::QrScanSchema {
        ui::QrScanSchema::User
    }

    fn try_parse(code: &str) -> Option<Self> {
        if let Ok((user_id, user_data_hash)) = decode_qr(code) {
            return Some(Self {
                user_id: user_id.hyphenated().to_string(),
                signup_extension: false,
                signup_extension_config: None,
                user_data_hash: Some(user_data_hash),
            });
        }
        if let Some(captures) = QR_CODE_V2.captures(code) {
            return Some(Data::from_v2(&captures));
        }
        #[cfg(feature = "internal-data-acquisition")]
        if let Some(captures) = QR_CODE_SIGNUP_EXTENSION.captures(code) {
            return Some(Data::from_signup_extension(&captures));
        }
        None
    }
}

impl Data {
    #[must_use]
    fn from_v2(captures: &Captures) -> Self {
        let user_id = captures
            .name("user_id")
            .expect("user_id capture group must be present")
            .as_str()
            .to_string();
        Self {
            user_id,
            signup_extension: false,
            signup_extension_config: None,
            user_data_hash: None,
        }
    }
```

**File:** src/backend/user_status.rs (L163-179)
```rust
    if let (Some(backend_keys), Some(user_data)) = (backend_keys, authenticated_app_data) {
        tracing::info!("User QR-data: {user_data:?}");

        #[cfg(not(feature = "skip-user-qr-validation"))]
        {
            let Some(user_data_hash) = &qr_code.user_data_hash else {
                tracing::error!(
                    "image_self_custody is provided by backend, but got no user_data_hash from \
                     QR-code"
                );
                return Ok(None);
            };
            if !user_data.verify(user_data_hash) {
                tracing::error!("user_data verification failure");
                return Ok(None);
            }
        }
```

**File:** src/backend/user_status.rs (L245-270)
```rust
    } else {
        // Using an old QR-code format.
        if qr_code.user_data_hash.is_some() {
            tracing::error!(
                "user_data_hash is provided by QR-code, but got no user_data from backend"
            );
            return Ok(None);
        }
        Ok(Some(UserData {
            backend_iris_public_key: None,
            backend_iris_encrypted_private_key: None,
            backend_normalized_iris_public_key: None,
            backend_normalized_iris_encrypted_private_key: None,
            backend_face_public_key: None,
            backend_face_encrypted_private_key: None,
            backend_tier2_public_key: None,
            backend_tier2_encrypted_private_key: None,
            self_custody_user_public_key: None,
            id_commitment: None,
            #[cfg(feature = "internal-data-acquisition")]
            data_policy: DataPolicy::FullDataOptIn,
            pcp_version: 0,
            user_centric_signup: false,
            orb_relay_app_id: None,
        }))
    }
```

**File:** src/backend/signup_post.rs (L125-133)
```rust
    let mut form = Form::new()
        .text("softwareVersion", &*ORB_OS_VERSION)
        .text("orbId", ORB_ID.as_str())
        .text("distributorId", operator_qr_code.user_id.clone())
        .text("userId", user_qr_code.user_id.clone())
        .text("region", s3_region.to_owned())
        .text("signature", signature.map_or(String::default(), Clone::clone))
        .text("codes", codes)
        .text("reason", signup_reason.to_screaming_snake_case().to_string());
```
