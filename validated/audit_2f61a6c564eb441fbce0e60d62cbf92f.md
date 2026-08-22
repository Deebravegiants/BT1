### Title
Iris-code signature omits `signup_id`, operator/distributor ID, and `signup_reason` from the signed payload, allowing a valid Secure-Element signature to be replayed across different signup contexts - (File: src/plans/enroll_user.rs)

### Summary
The reported bug class is that a cryptographic authorization (a signature) is computed over a subset of the parameters that actually determine the authorized action, so the same signature can be replayed against a different, unauthorized context (different `implementation` in the Solidity report). In `orb-core`, the analogous pattern occurs in the signup submission flow: the Secure-Element-backed "iris code signature" sent to the signup backend is computed only over the Orb ID, user QR-code `user_id`, and iris code/version fields, but the request that carries this signature also includes `signup_id`, the operator/distributor ID, and `signup_reason` — none of which are bound into the signed digest.

### Finding Description
`make_signature()` builds the signed digest as: [1](#0-0) 

```
ORB_ID + user_qr_code.user_id + ir_net_version + iris_version +
eye_left.{iris_code, mask_code, iris_code_version} + eye_right.{iris_code, mask_code, iris_code_version}
```

signed by the Secure Element via `secure_element::sign()` [2](#0-1) .

This resulting signature is then submitted to the backend alongside several other request parameters that are **not** part of the signed digest: the `signup_id` (used as the URL path parameter), `distributorId` (operator QR `user_id`), and `reason` (`SignupReason`: `Normal`, `Failure`, `Fraud`): [3](#0-2) 

The caller (`Plan::run`) computes the signature once from `(user_qr_code, pipeline)` and independently passes `signup_id`, `operator_qr_code`, and `signup_reason` to `signup_post::request`: [4](#0-3) 

Because `signup_id`, operator/distributor identity, and `signup_reason` are excluded from the signed digest, the signature only attests "this iris code belongs to this user, produced by this Orb" — it does not attest to *which signup session*, *which operator*, or *under what fraud/failure classification* the iris data is being submitted. A party able to influence or replay these unsigned fields (e.g. retry logic, a compromised/duplicated request path, or backend-side reordering) can attach a validly-Secure-Element-signed iris code to a different `signup_id`, different operator attribution, or a different `signup_reason` value than the one the signature was originally computed for — exactly the same "signature reusable in an unauthorized context because a binding parameter is missing from the hash" pattern as the ProxyFactory report.

### Impact Explanation
If exploited, this allows misattribution of a signup to a different `signup_id`/operator, or — more critically — allows a request whose `reason` field is switched between `Fraud`, `Failure`, and `Normal` while keeping the same orb-signed iris-code signature valid, since the signed payload never covers `reason`. This directly touches fraud enforcement: the backend's decision to treat a signup as fraudulent, failed, or normal relies on the unsigned `reason` field, so the SE signature provides no protection against tampering with the outcome classification of a signup, undermining the request-authenticity guarantee the signature is meant to provide for signup authorization / fraud-flagging.

### Likelihood Explanation
Likelihood is moderate: the request path is constructed and sent entirely within `orb-core` in-process (not attacker-controlled input at the API level), so remote unprivileged exploitation would require an ability to modify the outgoing multipart form fields after signature computation but before/at network transmission (e.g., a compromised or malicious component with write access to the request pipeline, or a replay of a captured request against a different `signup_id`/`reason`). Because the signature intentionally does not bind these fields, no cryptographic control prevents such tampering once request-construction integrity is bypassed, unlike the `iris_code`/`user_id`/`orb_id` fields, which are protected.

### Recommendation
Include `signup_id`, the operator/distributor `user_id`, and `signup_reason` in the SHA-256 context fed to `secure_element::sign()` in `make_signature()`, so the Secure-Element signature binds the exact signup session, operator attribution, and fraud/failure classification, preventing any reuse of a valid signature across different signups, operators, or reason codes.

### Proof of Concept
Conceptual reproduction based on the code paths cited above:
1. Orb captures iris data for `user_qr_code` and calls `make_signature(user_qr_code, pipeline)`, producing `signature = SE_sign(orb_id || user_id || iris codes...)` — note `signup_id`, `operator_qr_code`, and `signup_reason` are not included [1](#0-0) .
2. `Plan::run` sends this `signature` together with a specific `signup_id`, `operator_qr_code`, and `signup_reason::Fraud` via `signup_post::request` [5](#0-4) [6](#0-5) .
3. Because `signature` does not cryptographically bind `signup_id`, `distributorId`, or `reason`, the identical `signature` value remains valid if resubmitted with a different `signup_id` path, different `distributorId`, or `reason::Normal` instead of `Fraud` — the backend cannot detect the substitution using the signature alone, since the Secure Element never signed those fields.

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

**File:** src/secure_element.rs (L10-21)
```rust
/// Signs this buffer with Secure Element and returns the output.
#[cfg(not(test))]
pub fn sign<T: AsRef<[u8]>>(data: T) -> Result<Vec<u8>> {
    fn inner(data: &[u8]) -> Result<Vec<u8>> {
        let encoded = BASE64.encode(data);

        tracing::info!("Running orb-sign-iris-code");
        let mut command = Command::new("/usr/bin/orb-sign-iris-code");
        command.stdin(Stdio::piped());
        command.stdout(Stdio::piped());
        command.stderr(Stdio::piped());
        let mut child = command.spawn().wrap_err("running orb-sign-iris-code")?;
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
