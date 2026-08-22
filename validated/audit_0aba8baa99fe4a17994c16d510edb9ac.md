### Title
Attestation signature in `make_signature` lacks `signup_id`/session binding, enabling cross-signup replay - ([File: src/plans/enroll_user.rs])

### Summary
`make_signature` in `src/plans/enroll_user.rs` builds the secure-element-signed digest solely from `ORB_ID`, `user_qr_code.user_id`, and the iris/mask code fields of the biometric pipeline, with no `signup_id` or timestamp mixed into the hash. Two separate signup sessions for the same user QR code that produce the same biometric pipeline output (e.g., replaying the same static iris artifact) will therefore be signed over the exact same SHA-256 digest, meaning the resulting attestation is not cryptographically bound to a specific `signup_id`.

### Finding Description
The call chain is `Plan::run` (src/plans/enroll_user.rs:72-88) spawning `make_signature(&user_qr_code, &pipeline)` on a blocking task, which builds the digest: [1](#0-0) 

This digest is composed only of `ORB_ID`, `user_qr_code.user_id`, `ir_net_version`, `iris_version`, and each eye's `iris_code`/`mask_code`/`iris_code_version`. Notably absent are `signup_id` (passed separately to `Plan::run` at src/plans/enroll_user.rs:60 and only used later to call `signup_post::request`) and any timestamp/nonce. [2](#0-1) 

The `signup_id` is only used as a URL path segment and as an out-of-band field in the multipart form sent to the backend via `signup_post::request`: [3](#0-2) 

Because `signup_id` and any capture-session-unique nonce are never mixed into the signed digest, the message that the secure element signs is identical for any two signups that share the same `user_id` and produce identical iris/mask codes/versions. If an attacker forces the biometric pipeline to reproduce the same `iris_code`/`mask_code`/`iris_code_version` twice (e.g. presenting the same static/printed iris artifact for the same user QR code across two signup attempts), the SHA-256 digest fed to `secure_element::sign` is byte-for-byte identical in both signups. Whether the two ECDSA signature *bytes* end up bit-identical depends on the nonce-generation used by the underlying signer, but the vulnerability itself does not require byte-identical signatures — it requires only that a signature generated for signup A cryptographically validates the exact same message that signup B would send, since neither the message nor the signature carries any signup-session-unique commitment. This breaks the intended "attestation must not be replayable across signups" invariant at the orb-core level: nothing in this code path prevents the same attestation message/signature from being valid for more than one `signup_id`.

### Impact Explanation
This matches the "Attestation forgery / cross-signup replay" impact category noted in the audit scope: an unprivileged attacker who can trigger two signups with the same user QR-code and reproduce the same iris capture can obtain a secure-element-signed attestation whose cryptographic content is indistinguishable across signup sessions. If the backend's fraud/duplicate detection or session-linking logic relies on the signature as a session-unique proof-of-capture (rather than solely on the out-of-band `signup_id` path parameter), this weakens the guarantee that the signed material was freshly captured for that specific signup attempt.

### Likelihood Explanation
Preconditions are modest and within the unprivileged threat model given in the prompt: the attacker only needs to run two signup sessions using the same user QR code and present the same iris artifact (e.g., a printed/static iris image reproduced twice) to the camera, which is exactly the "scene shown to the cameras" attack surface called out in the rules. No key leakage, no MCU tampering, and no operator access are required — repeatability depends only on the biometric pipeline deterministically reproducing identical `iris_code`/`mask_code` bytes for the same physical artifact, which is plausible for a static replay input.

### Recommendation
Bind the signed digest to the specific signup session by including `signup_id` (and ideally a freshness element such as a timestamp or per-signup nonce) inside the `Context` before calling `secure_element::sign` in `make_signature`, e.g. `ctx.update(signup_id.as_bytes())`. Update `Plan::run` to pass `self.signup_id` into `make_signature` so the attestation is cryptographically tied to one signup attempt and cannot be reproduced identically (in content) across two distinct signups.

### Proof of Concept
Unit test in `src/plans/enroll_user.rs` (or a new test module) demonstrating that the signed digest input is independent of `signup_id`:
1. Construct a `qr_scan::user::Data` with a fixed `user_id` and a `Pipeline` with fixed `iris_code`/`mask_code`/`iris_code_version`/`iris_version`/`ir_net_version` for both eyes.
2. Call `make_signature(&user_qr_code, &pipeline)` twice, simulating two different signup attempts (two different `SignupId`s used only in the surrounding `Plan`, not passed into `make_signature`).
3. Assert that the SHA-256 digest constructed inside `make_signature` (expose it via a test-only helper, or reconstruct the same `Context` update sequence in the test) is identical for both calls, and that `secure_element::sign` (test impl in `src/secure_element.rs`) validates successfully against that same digest for both "signups" — proving the signed content carries no `signup_id` binding regardless of whether the raw ECDSA signature bytes differ due to nonce randomization. [4](#0-3)

### Citations

**File:** src/plans/enroll_user.rs (L90-102)
```rust
        let signup_id = self.signup_id.to_string();
        for i in 0..RETRIES_COUNT {
            let response = signup_post::request(
                signature.as_ref(),
                &signup_id,
                &self.operator_qr_code,
                &self.user_qr_code,
                &self.s3_region_str,
                self.capture,
                self.pipeline,
                self.signup_reason,
            )
            .await;
```

**File:** src/plans/enroll_user.rs (L290-304)
```rust
fn make_signature(user_qr_code: &qr_scan::user::Data, pipeline: &Pipeline) -> Result<String> {
    let mut ctx = Context::new(&SHA256);
    ctx.update(ORB_ID.as_str().as_bytes());
    ctx.update(user_qr_code.user_id.as_bytes());
    ctx.update(pipeline.v2.ir_net_version.as_bytes());
    ctx.update(pipeline.v2.iris_version.as_bytes());
    ctx.update(pipeline.v2.eye_left.iris_code.as_bytes());
    ctx.update(pipeline.v2.eye_left.mask_code.as_bytes());
    ctx.update(pipeline.v2.eye_left.iris_code_version.as_bytes());
    ctx.update(pipeline.v2.eye_right.iris_code.as_bytes());
    ctx.update(pipeline.v2.eye_right.mask_code.as_bytes());
    ctx.update(pipeline.v2.eye_right.iris_code_version.as_bytes());
    let signed = secure_element::sign(ctx.finish())?;
    Ok(BASE64.encode(&signed))
}
```

**File:** src/backend/signup_post.rs (L125-143)
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
    if let Some(latitude) = capture.latitude {
        form = form.text("latitude", latitude.to_string());
    }
    if let Some(longitude) = capture.longitude {
        form = form.text("longitude", longitude.to_string());
    }
    let request = super::client()?
        .post(format!("{}/api/v2/signups/{signup_id}", *SIGNUP_BACKEND_URL))
        .basic_auth(&*ORB_ID, Some(get_orb_token()?))
        .multipart(form);
```

**File:** src/secure_element.rs (L58-62)
```rust
#[cfg(test)]
pub fn sign<T: AsRef<[u8]>>(data: T) -> Result<Vec<u8>> {
    let pkey = SIGNING_KEY.lock().unwrap();
    Ok(openssl::ecdsa::EcdsaSig::sign(data.as_ref(), &*pkey).unwrap().to_der().unwrap())
}
```
