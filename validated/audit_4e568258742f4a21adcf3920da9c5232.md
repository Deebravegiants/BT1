### Title
`make_signature()` excludes `signup_reason`, `distributorId`, and other request fields from the signed payload, allowing post-signature tampering — ([File: src/plans/enroll_user.rs])

### Summary
`make_signature()` computes a secure-element-backed signature over only a subset of the data that is ultimately submitted to the backend signup endpoint. Fields such as the operator/distributor identity, signup reason, and geolocation are sent in the same request but are **not** covered by the signature, so they can be altered without invalidating the cryptographic attestation — the same "hash omits a security-relevant field" root cause as the referenced `IMultiSourceLoan.loan.hash()` bug (missing `protocolFee`).

### Finding Description
`make_signature()` hashes and signs only: `ORB_ID`, `user_qr_code.user_id`, the pipeline `ir_net_version`/`iris_version`, and both eyes' `iris_code`/`mask_code`/`iris_code_version`: [1](#0-0) 

That signature is then submitted together with several other fields via `signup_post::request`, most notably `distributorId` (derived from `operator_qr_code.user_id`), `reason` (the `SignupReason`), and `region`/`latitude`/`longitude` — none of which are part of the signed digest: [2](#0-1) 

The `SignupReason` enum explicitly distinguishes `Normal` from `Fraud`, and this reason is what the backend uses to decide how to process/flag the signup: [3](#0-2) 

Because the secure-element signature (the only cryptographic attestation binding the iris biometrics to a specific submission) does not cover `reason` or `distributorId`, any code path that constructs the multipart form after the signature has been produced can change these values without the signature verification failing — mirroring exactly the `loan.hash()` case, where `_baseLoanChecks()` accepted a `protocolFee` that wasn't part of the hash and thus could be freely altered.

### Impact Explanation
- **Misattributed signup / identity binding failure**: `distributorId` (the operator/referrer id credited for the signup) is not bound to the signature, so the operator identity attached to a signed biometric enrollment is not cryptographically tied to that enrollment.
- **Fraud-flag bypass**: `signup_reason` (`Normal`/`Failure`/`Fraud`) is likewise excluded from the signed payload. Since the orb's own fraud detection sets this field, and it isn't attested by the secure element, a divergence between what was signed and what was reported as `reason` cannot be detected by verifying the signature alone.

This matches the "misattributed signup" and "fraud bypass" impact categories, analogous to the confirmed Medium-severity Gondi finding where an unhashed `protocolFee` allowed fee evasion/accounting errors.

### Likelihood Explanation
Exploitability depends on there being a code path or intermediary between where `make_signature()` runs (secure element) and where `signup_post::request()` assembles the form that can independently control `signup_reason`/`operator_qr_code` after signing. In the current single-process flow in `Plan::run`, the same in-memory struct fields are used for both, so this is primarily a **defense-in-depth / trust-boundary gap** rather than a directly demonstrated remote exploit in this codebase as currently wired: [4](#0-3) . I was not able to fully verify from the indexed code whether any other component (e.g., a later mutation of `signup_reason` after signature computation, or an IPC/plan-mod path under the `allow-plan-mods` feature) can modify these fields post-signing before submission — this would need further investigation, ideally with a full Devin session against the complete repository.

### Recommendation
Extend `make_signature()` to include all security/attribution-relevant fields that are transmitted alongside it — at minimum `signup_reason`, `operator_qr_code.user_id` (distributorId), and `signup_id` — in the signed digest, so the backend can reject any request where these fields don't match what was attested by the secure element:
```rust
fn make_signature(
    user_qr_code: &qr_scan::user::Data,
    operator_qr_code: &qr_scan::user::Data,
    signup_reason: SignupReason,
    signup_id: &str,
    pipeline: &Pipeline,
) -> Result<String> {
    let mut ctx = Context::new(&SHA256);
    ctx.update(ORB_ID.as_str().as_bytes());
    ctx.update(user_qr_code.user_id.as_bytes());
    ctx.update(operator_qr_code.user_id.as_bytes());
    ctx.update(signup_reason.to_screaming_snake_case().as_bytes());
    ctx.update(signup_id.as_bytes());
    // ... existing iris/pipeline fields ...
}
```

### Proof of Concept
1. `Plan::run` computes `signature = make_signature(&user_qr_code, &pipeline)` covering only `user_id` + iris codes: [5](#0-4) .
2. The same call passes `self.operator_qr_code`, `self.signup_reason`, and `self.s3_region_str` into `signup_post::request`, which places them into the multipart form as `distributorId`, `reason`, and `region` alongside the (unrelated) `signature` field: [6](#0-5) .
3. Any downstream mutation of `signup_reason` or `operator_qr_code` (e.g., between fraud detection setting `SignupReason::Fraud` and form submission) is not covered by the signature, so backend-side signature verification cannot detect the discrepancy — analogous to `repayLoan(loan.protocolFee=0)` escaping fees because `protocolFee` wasn't part of `loan.hash()`.

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

**File:** src/backend/signup_post.rs (L72-96)
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

/// Converts the signup reason to screaming snake case.
impl SignupReason {
    /// Converts the signup reason to screaming snake case. Using Serde's renaming won't work because Serde
    /// automatically adds "" (quotes) to the produced string. I.e. the output from Serde is "\"NORMAL\"".
    #[must_use]
    pub fn to_screaming_snake_case(&self) -> &str {
        match self {
            SignupReason::Normal => "NORMAL",
            SignupReason::Failure => "FAILURE",
            SignupReason::Fraud => "FRAUD",
        }
    }
}
```

**File:** src/backend/signup_post.rs (L125-139)
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
```
