### Title
Secure-element signup signature omits `signup_id`, enabling replay across signup sessions - (File: `src/plans/enroll_user.rs`)

### Summary
The signature that binds an Orb's secure-element attestation to a signup is computed by `make_signature` in `src/plans/enroll_user.rs`, but the hash it signs does not include the `signup_id` that uniquely identifies the signup session/request. This mirrors the reported EIP712 replay bug where the signed payload omits the `batchId` and only an unrelated nonce is checked — here, the signed payload omits the `signup_id`, while the backend endpoint that consumes the signature is keyed only by `signup_id` in the URL path, not by the signature content itself.

### Finding Description
`make_signature` builds a SHA-256 digest over `ORB_ID`, the user's QR `user_id`, and biometric pipeline fields (iris/mask codes, versions), then signs it with the secure element: [1](#0-0) 

This signature, together with the same biometric `codes` payload, is submitted via `signup_post::request` to `POST /api/v2/signups/{signup_id}`, where `signup_id` is a path parameter separate from the signed data: [2](#0-1) 

Because `signup_id` is never hashed or otherwise cryptographically bound to the signature, the signature+codes pair produced for one signup attempt is valid input for any other request bearing a different `signup_id`, exactly as the batchId was omitted from `encodeTransactionData` in the referenced report while the contract only checked `nonces[batchId]`. The call site confirms `signup_id` and the `signature` are independent parameters passed together but never cross-checked: [3](#0-2) 

### Impact Explanation
Anyone able to submit signup requests to the signup backend endpoint with a previously captured `(signature, codes)` pair can resubmit that exact secure-element-signed attestation under a new `signup_id`, without needing the secure element to sign anything again. This allows misattribution/duplication of a genuine biometric-capture attestation across multiple signup sessions — the cryptographic proof no longer uniquely certifies "this specific signup", enabling cross-signup replay of a valid secure-element signature and undermining the signup authorization/identity-binding guarantee the signature was meant to provide.

### Likelihood Explanation
Exploitation only requires observing one legitimate `(signature, codes)` submission (e.g., via network capture or backend logs/telemetry) and issuing another signup POST with a different `signup_id` and the same signature/codes — no secure-element access or privileged Orb credentials beyond what is already needed to reach the signup endpoint are required. This is a direct code-level omission (missing domain-separation field), not a cryptographic break, matching the "unbounded first-transaction replay" pattern from the reference report.

### Recommendation
Include `signup_id` (and ideally a monotonic/anti-replay nonce) in the data hashed by `make_signature` before signing, and have the backend validate that the signature's embedded `signup_id` matches the `signup_id` used in the request path, so a captured signature cannot be replayed under a different signup session.

### Proof of Concept
1. Capture a legitimate signup submission's `signature` and `codes` form fields from `signup_post::request` (e.g., via network inspection) for `signup_id = A`.
2. Issue a new `POST /api/v2/signups/{signup_id=B}` request reusing the identical `signature` and `codes` values (all other fields identical or attacker-controlled) — since `make_signature` never hashed `signup_id`, the previously valid secure-element signature verifies successfully for the new `signup_id`.
3. The backend accepts the attestation as authentic for signup `B`, even though it was never actually produced by the secure element for that session.

### Citations

**File:** src/plans/enroll_user.rs (L72-102)
```rust
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

**File:** src/backend/signup_post.rs (L98-143)
```rust
/// Makes a signup request.
#[allow(clippy::too_many_arguments)]
pub async fn request(
    signature: Option<&String>,
    signup_id: &str,
    operator_qr_code: &qr_scan::user::Data,
    user_qr_code: &qr_scan::user::Data,
    s3_region: &str,
    capture: &Capture,
    pipeline: Option<&Pipeline>,
    signup_reason: SignupReason,
) -> Result<Response> {
    dd_gauge!(
        "main.gauge.signup.sharpest_iris",
        capture.eye_left.ir_net_estimate.score.to_string(),
        "side:left"
    );
    dd_gauge!(
        "main.gauge.signup.sharpest_iris",
        capture.eye_right.ir_net_estimate.score.to_string(),
        "side:right"
    );
    tracing::info!("Orb OS version: {:?}", &*ORB_OS_VERSION);
    tracing::info!("Signup reason: {:?}", signup_reason);
    let codes = pipeline.map_or(String::new(), |p| {
        serde_json::to_string_pretty(&format_pipeline(p)).expect("always a valid JSON")
    });
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
