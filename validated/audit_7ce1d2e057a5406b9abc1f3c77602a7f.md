### Title
`make_signature` omits `signup_id`/session nonce from the signed digest, enabling attestation replay across signups - ([File: src/plans/enroll_user.rs])

### Summary
`make_signature` in `src/plans/enroll_user.rs` builds the SHA-256 digest that is handed to `secure_element::sign` from only `ORB_ID`, `user_qr_code.user_id`, and the pipeline's iris/mask codes and version strings. No `signup_id` (or any other session-unique nonce) is ever fed into the `Context::update` sequence, so the digest — and therefore the secure-element signature over it — is a pure function of `(orb_id, user_id, iris/mask codes, versions)` and is completely independent of which signup session produced it.

### Finding Description
The signing path is:
`enroll_user::Plan::run` → `make_signature(&user_qr_code, &pipeline)` → `secure_element::sign(ctx.finish())`. [1](#0-0) 

`make_signature` never receives or hashes `self.signup_id` (an `orb_wld_data_id::SignupId` that is otherwise available on the `Plan` struct and used only as the URL path segment in `signup_post::request`): [2](#0-1) 

The resulting signature is uploaded as a plain `signature` form field, decoupled from the `signup_id` used only for HTTP routing (`/api/v2/signups/{signup_id}`): [3](#0-2) 

Because `signup_id` (or any other session/nonce value) never enters the hashed context, two sequential signups performed by the same attacker-controlled `user_qr_code.user_id`, whose iris/mask codes and pipeline versions happen to match (e.g., a captured/replayed identical package, or genuinely stable iris code output from repeated captures of the same eyes with the same pipeline version), produce byte-identical digests and therefore signatures that are not bound to a particular signup session. This violates the stated property that "attestation is authentic … must not be replayable across signups," since the orb-core side does nothing cryptographically to prevent a signature produced for signup A being reused/submitted for signup B.

### Impact Explanation
Scoped impact is a forged/reused secure-element attestation: a signature legitimately produced during one signup session can be replayed and presented as valid for a different signup session for the same `user_id`/iris package, without the secure element re-attesting per-session. This undermines the anti-replay guarantee of the signing scheme and could be leveraged to bypass session-specific backend checks that assume the signature is freshly minted for the specific `signup_id` being submitted (e.g., resubmitting a prior valid signature to legitimize a package under a new signup attempt after a fraud/liveness re-check failure in the second session). This matches an "attestation forgery / replay across signups" impact category.

### Likelihood Explanation
Preconditions: the attacker must control (or repeat) `user_qr_code.user_id` and be able to complete multiple signups on the same Orb (both explicitly allowed per the question's threat model). Whether the identical-digest condition is trivially reachable depends on whether the biometric pipeline yields bit-identical iris/mask codes across two separate capture sessions with the same versions — this is plausible but not guaranteed to be attacker-controlled deterministically. Regardless, the core weakness — absence of `signup_id`/nonce in the signed digest — is unconditionally present in the code and demonstrable independent of biometric variability, since `make_signature` does not take `signup_id` as an input at all. Whether backend-side verification (outside this repo) independently binds the signature to `signup_id` cannot be confirmed here, which limits certainty of full exploitability but does not change the fact that orb-core itself provides no cryptographic session binding.

### Recommendation
Include the `signup_id` (or a fresh per-signup nonce/timestamp) in the `Context::update` sequence inside `make_signature`, e.g. `ctx.update(signup_id.to_string().as_bytes())`, before signing, and require the backend to verify that the signed digest matches the `signup_id` in the request path/body. This binds the secure-element attestation to a single signup session and prevents replay across sessions.

### Proof of Concept
Unit test in `src/plans/enroll_user.rs` (or a test module with access to `make_signature`, `qr_scan::user::Data`, and `biometric_pipeline::Pipeline`):
1. Construct one `user_qr_code` and one `pipeline` with fixed iris/mask codes and versions.
2. Call `make_signature(&user_qr_code, &pipeline)` twice, simulating two different signup sessions (conceptually `signup_id_a != signup_id_b`), noting that the function signature never accepts `signup_id`.
3. Assert that the underlying digest bytes fed to `secure_element::sign` (or the resulting base64 signature under the deterministic test signer) are identical in both calls, proving `signup_id` has zero influence on the signed material.
4. Expected assertion: `digest_a == digest_b` (and, using the test `secure_element::sign` deterministic-enough setup, `signature_a` can be replayed for `signup_id_b`'s upload), demonstrating the missing per-session binding described above.

### Citations

**File:** src/plans/enroll_user.rs (L59-90)
```rust
pub struct Plan<'a> {
    pub signup_id: SignupId,
    pub operator_qr_code: qr_scan::user::Data,
    pub user_qr_code: qr_scan::user::Data,
    pub s3_region_str: String,
    pub capture: &'a Capture,
    pub pipeline: Option<&'a Pipeline>,
    pub signup_reason: SignupReason,
}

impl Plan<'_> {
    /// Runs the user enrollment plan.
    #[allow(clippy::too_many_lines)]
    pub async fn run(self, orb: &mut Orb) -> Status {
        let user_qr_code = self.user_qr_code.clone();
        let signature = if let Some(p) = self.pipeline.cloned() {
            match task::spawn_blocking(move || make_signature(&user_qr_code, &p)).await {
                Ok(Ok(signature)) => Some(signature),
                Ok(Err(err)) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
                Err(err) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
            }
        } else {
            None
        };
        tracing::info!("Iris code signature: {:?}", signature);
        let signup_id = self.signup_id.to_string();
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
