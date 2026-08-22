I found a genuine analog of this bug class in orb-core's signup attestation flow.

### Title
Secure-element signature over signup data omits `signup_reason`, operator ID, and geolocation fields, allowing their tampering without invalidating the biometric attestation - (File: `src/plans/enroll_user.rs`)

### Summary
Similar to the `FeeRefund.tokenGasPriceFactor` bug, where a value used in a security-critical calculation was excluded from the signed payload, orb-core computes a secure-element signature over only a subset of the fields that are ultimately submitted to the signup backend. Critical fields that affect fraud classification and signup attribution are sent unsigned alongside the signature, so anything that can modify the outgoing request after signing (but before it reaches the backend) can alter those fields without breaking the attestation.

### Finding Description
`make_signature()` hashes only the Orb ID, user QR-code ID, and iris pipeline codes/versions, then signs the digest with the secure element: [1](#0-0) 

This signature is passed as the `signature` field to `signup_post::request()`, which builds a multipart form containing several *additional* fields that are **not** part of the signed digest: `distributorId` (operator ID), `region`, `latitude`, `longitude`, and — notably — `reason` (the `SignupReason`, which can be `Normal`, `Failure`, or `Fraud`): [2](#0-1) 

`SignupReason::Fraud` is explicitly documented as tagging a signup that "was detected as a fraud attempt at the orb": [3](#0-2) 

Because the secure-element signature covers only the iris-code/version material and not `reason`, `distributorId`, or the geolocation fields, the cryptographic attestation cannot detect if these values are altered between the point where `make_signature()` runs and the point where the HTTP form is actually transmitted in `enroll_user::Plan::run()`: [4](#0-3) 

The secure element is specifically used here (as opposed to a plain software hash) to create a hardware-rooted trust boundary that should make biometric submissions resistant to software-level tampering. Because fraud classification, operator attribution, and location data sit outside that signed boundary, they remain forgeable by anything capable of intercepting or modifying the outbound multipart request without needing to compromise the secure element itself — directly mirroring the `tokenGasPriceFactor` case where the "submitter" could rewrite an unsigned parameter after the user-approved values were signed.

### Impact Explanation
An actor able to modify the outgoing signup request post-signing (e.g., a compromised software component sitting between the signature step and the network send, or interception at the HTTP layer) can flip a signup that the Orb classified as `Fraud` into `Normal`, reassign the `distributorId` to a different operator, or alter the reported geolocation — all without invalidating the biometric signature the backend relies on as an integrity attestation. This constitutes an attestation-forgery / fraud-enforcement-bypass condition: the backend's trust in the signature does not extend to the very field (`reason`) that flags fraudulent signups.

### Likelihood Explanation
Exploitation requires the ability to intercept/modify the constructed multipart form between signature computation and the HTTP request being sent — the same capability level as the original relayer in the referenced report (control over data after signing, before submission), not physical hardware access to the secure element. Given that `reason`, `distributorId`, and location are all trivially attacker-controllable string/numeric form fields with zero cryptographic linkage to the signature, this is a straightforward class of tampering once that interception capability exists.

### Recommendation
Include `signup_reason`, `distributorId` (operator ID), and any location fields relied upon by the backend for fraud/attribution decisions in the data hashed and signed in `make_signature()` (mirroring the fix recommended for `tokenGasPriceFactor`: bind all security-relevant fields to the signature), and have the backend verify the signature against the exact submitted values for these fields, not just the iris codes.

### Proof of Concept
1. Orb detects a fraud attempt and sets `signup_reason = SignupReason::Fraud`.
2. `make_signature()` is called and only hashes `ORB_ID`, `user_qr_code.user_id`, and pipeline iris code fields — `signup_reason` is excluded: [1](#0-0) 
3. `signup_post::request()` is later called with the *original* signature but the `reason` field set independently as `signup_reason.to_screaming_snake_case()`: [5](#0-4) 
4. Anything able to alter the `reason` (or `distributorId`/`latitude`/`longitude`) form field before the HTTP request reaches the backend produces a request that still carries a valid signature, because that signature never covered these fields.

### Citations

**File:** src/plans/enroll_user.rs (L69-101)
```rust
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

**File:** src/backend/signup_post.rs (L72-82)
```rust
/// Every signup needs to be tagged with a reason for the backend to process it.
#[derive(Serialize, Debug, Default, Copy, Clone, PartialEq, Eq)]
pub enum SignupReason {
    /// Signup was successfully processed on the Orb.
    #[default]
    Normal,
    /// Signup failed due to some agent dying in the biometric pipeline or some internal error.
    Failure,
    /// Signup was detected as a fraud attempt at the orb (not to be confused with the backend fraud checks).
    Fraud,
}
```

**File:** src/backend/signup_post.rs (L99-139)
```rust
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
```
