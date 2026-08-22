### Title
Insufficiently bound iris-code signature enables cross-signup replay/misattribution - (File: `src/plans/enroll_user.rs`)

### Summary
The reported bug class describes a Fiat-Shamir/challenge value that is derived from too little context, letting a party that controls part of the input reuse or misapply a validly-derived value across a different session than the one it was intended for. In orb-core, the closest reachable analog is `make_signature` in `src/plans/enroll_user.rs`, which builds the secure-element-signed binding between a user QR-code identity and the captured iris codes for a signup, but the hashed payload omits the `signup_id`, `timestamp`, and `operator_qr_code` that distinguish one signup session from another.

### Finding Description
`make_signature` computes a SHA-256 digest over `ORB_ID`, the user QR-code `user_id`, and the iris/mask codes and versions for both eyes, then has the secure element sign that digest: [1](#0-0) . This signed blob is what is submitted to the backend as proof that a specific `(user_id, iris_code)` pairing was produced and attested on this Orb, via the `signature` form field in `signup_post::request`: [2](#0-1) .

Crucially, the signed digest does not include the `signup_id` that uniquely identifies the specific signup session (`self.signup_id.to_string()` is only used afterwards to route the HTTP request, not fed into `make_signature`): [3](#0-2) . It also excludes the `operator_qr_code` (which attributes the signup to a specific operator/distributor) and any timestamp or nonce that would bind the signature to a single request attempt. This mirrors the reported bug class: the value used by the verifier (the backend) to attest authenticity is derived from an insufficient subset of the data that actually distinguishes one verification context from another, and the party assembling the hashed data (the orb software/runtime) controls exactly which fields go into that binding.

Because `user_id`, iris codes, and code versions are the only inputs, the exact same signed value can be legitimately produced once and then resubmitted verbatim in `signup_post::request` for a different `signup_id`, in retried requests over `RETRIES_COUNT` iterations, or replayed by any process able to intercept/store the multipart form (the `signature` text field): [4](#0-3) . If the backend's authenticity check relies on this signature alone to validate that the reported iris codes belong to the claimed `user_id` for the specific request in question, the missing session-binding fields let a previously captured signed blob be attached to a new/different signup context.

### Impact Explanation
A replayed/misapplied signature could let a compromised or malicious orb-side component resubmit a validly-signed `(user_id, iris_code)` attestation under a different `signup_id` or operator association than the one for which it was originally produced, causing the backend to accept an enrollment as authentically attested when the actual capture context differs from what is claimed. This is a cross-signup misattribution risk: the biometric data and its cryptographic attestation are not scoped to a single enrollment attempt.

### Likelihood Explanation
The likelihood depends entirely on backend-side validation, which is outside the orb-core repository and cannot be inspected here. If the backend independently binds the signature to `signup_id` and rejects duplicates/replays, the impact is contained; if it trusts the signature purely for the `(orbId, userId, iris codes)` binding (as the on-device hash suggests it should), replay across signup attempts becomes straightforward. This exposure is therefore plausible but not fully provable from the orb-core code alone.

### Recommendation
Include the `signup_id`, a fresh timestamp/nonce, and ideally the `operator_qr_code`/distributor identity in the data hashed and signed by `make_signature`, so the secure-element signature is cryptographically bound to the exact signup session it is used for, preventing replay or reattachment to a different session.

### Proof of Concept
Conceptual PoC (not executable without backend access):
1. Perform signup A with `user_id=U`, iris codes `C`; orb computes `signature = Sign(H(ORB_ID || U || iris/mask codes))` via `make_signature`.
2. Capture/store the resulting `signature` string sent in the multipart form of `signup_post::request` for signup A.
3. Initiate a second signup attempt B (different `signup_id`, potentially different operator) with the same `user_id=U` and iris codes `C` (e.g., replaying/tampering with the request), attaching the previously captured `signature`.
4. Because `signature` never encoded `signup_id` or operator context, the backend—if it validates only the hash inputs shown in `make_signature`—cannot distinguish request B's session from request A's, potentially accepting an attestation that does not correspond to the actual capture context of B. [1](#0-0) [5](#0-4) [2](#0-1)

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

**File:** src/backend/signup_post.rs (L98-133)
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
```
