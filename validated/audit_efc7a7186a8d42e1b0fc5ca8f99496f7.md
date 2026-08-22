### Title
Signup signature omits `distributorId`, `signup_id`, and `reason` fields, allowing unauthorized tampering without invalidating the cryptographic signature - (File: `src/plans/enroll_user.rs`)

### Summary
The `make_signature` function that produces the cryptographic signature accompanying every signup request only hashes the orb ID, the user's QR user-id, and the pipeline/iris-code data. It excludes several fields that are sent alongside the signature in the same multipart request — the operator/distributor id, the `signup_id`, and the `signup_reason` — so these values can be swapped after signing without breaking signature verification, mirroring the reported `Order` bug class where fields used at settlement time were excluded from the signed payload.

### Finding Description
`make_signature` in `src/plans/enroll_user.rs` builds the signed digest from a fixed, narrow set of inputs: [1](#0-0) 

This signature is computed in `Plan::run` and then forwarded, together with several *other, unsigned* values, to `signup_post::request`: [2](#0-1) 

`signup_post::request` builds the actual multipart form sent to the backend. Note that `distributorId` (`operator_qr_code.user_id`), the `signup_id` (used in the URL path), `region`, `latitude`/`longitude`, and `reason` (`SignupReason`, e.g. `NORMAL`/`FRAUD`) are all included in the outgoing request but are never part of the hashed/signed bytes: [3](#0-2) 

Because the backend can only cryptographically validate the fields that were actually included in the signature (orb id, user id, iris/mask codes, pipeline versions), any process or channel able to modify the outgoing form data after the signature is computed — but before/while it reaches the backend — can change `distributorId`, `signup_id`, or `reason` while the signature still verifies successfully. This is structurally identical to the reported bug: fields consumed at "settlement"/processing time (`toRecipient`/`toTrader` in the report; `distributorId`/`signup_id`/`reason` here) are excluded from the signed data, so tampering with them is undetectable by signature verification alone.

### Impact Explanation
- Altering `reason` from `FRAUD` to `NORMAL` (or vice versa) without invalidating the signature would let a signup that the orb flagged as fraudulent be reported to the backend as a legitimate, successfully verified signup — a direct fraud-enforcement bypass, since the backend's only cryptographic guarantee covers the iris/mask codes, not the reason tag.
- Altering `distributorId` allows a signup's cryptographically-verified biometric data to be misattributed to a different operator/referrer than the one that actually performed the signup, an unauthorized/misattributed-signup scenario.
- Altering `signup_id` (transmitted in the URL, not the signed body) could let a validly signed iris-code payload be associated with a different signup session than the one it was captured for, corrupting per-signup record integrity (cross-signup state bleed).

### Likelihood Explanation
Exploitation requires the ability to modify the outgoing signup request after `make_signature` runs but before/while it is transmitted — e.g., a compromised or malicious component in the orb's own process/IPC pipeline that has access to the already-computed signature and the request-building code path, since `signature`, `operator_qr_code`, `signup_reason`, and `signup_id` are passed as independent parameters into `signup_post::request` rather than being cryptographically bound together. This does not require breaking the underlying ECDSA scheme — only interposing between signature computation and dispatch, which is a materially lower bar than forging a signature.

### Recommendation
Include `distributorId` (`operator_qr_code.user_id`), `signup_id`, and `signup_reason` (and any other field relied upon by backend processing) in the data hashed by `make_signature`, so the backend can verify that these fields have not been altered from what was originally signed by the secure element, analogous to the report's recommendation to include `toRecipient`/`toTrader` in the order signature or pass them explicitly and verifiably at settlement time.

### Proof of Concept
1. During a signup, the orb computes `signature = make_signature(&user_qr_code, &pipeline)` covering only `ORB_ID`, `user_qr_code.user_id`, and iris/mask codes (`src/plans/enroll_user.rs:290-304`).
2. `signup_post::request` is called with this `signature` plus separately-supplied `operator_qr_code`, `signup_id`, and `signup_reason` (`src/plans/enroll_user.rs:91-102`, `src/backend/signup_post.rs:100-133`).
3. If any component or channel between signature computation and network dispatch swaps `operator_qr_code.user_id`, the `signup_id` path segment, or `signup_reason`'s value, the backend still receives the original, validly-signed `signature`, `orbId`, and iris codes — verification of the signature succeeds even though `distributorId`/`signup_id`/`reason` were changed, because none of these three fields are part of the hashed input.

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
