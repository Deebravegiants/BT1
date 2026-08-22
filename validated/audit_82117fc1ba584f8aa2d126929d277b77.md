Confirmed: `SignupId::new` generates a fresh random 10-byte identifier per signup attempt via `thread_rng().gen()`, so each signup session has its own unique `signup_id`, but that identifier is never mixed into the signed digest computed in `make_signature`. [1](#0-0) [2](#0-1) 

### Title
Secure-element iris-code signature lacks signup-instance/session binding, enabling cross-signup replay - (File: src/plans/enroll_user.rs)

### Summary
The Orb's signup flow signs a digest of `ORB_ID`, the user's QR `user_id`, and the iris/mask codes with the hardware Secure Element in `make_signature`, then attaches this signature to the signup POST request. The signed digest never includes the freshly generated, per-attempt `signup_id`, the `distributorId` (operator), the `signup_reason`, or any timestamp/nonce, so the exact same signature bytes remain valid for any signup instance that reuses the same `orbId`/`userId`/iris-code payload, mirroring the eth-bridge finding where signature schemes omitted contract-instance/chain identifiers and were reusable across deployments/forks.

### Finding Description
`make_signature` builds the SHA-256 digest from `ORB_ID`, `user_qr_code.user_id`, and pipeline iris/mask code fields only, then has the Secure Element sign it: [2](#0-1) 
This signature is submitted to the backend alongside the `signup_id` in `signup_post::request`, but `signup_id` is passed only as a URL path/multipart parameter — it is not part of the signed material: [3](#0-2) 
Each signup attempt receives a fresh, randomly-generated `SignupId` via `SignupId::new`, meaning the system already has a natural per-instance identifier available, but it is never incorporated into the Secure-Element-signed message: [1](#0-0) 
Because the signature is a deterministic function of `(orbId, userId, iris/mask codes, versions)` with no domain separator for the specific signup session, capturing one valid signed request (e.g., via a compromised backend log, a proxy, or a replayed HTTP body) is sufficient to reproduce a "hardware-signed" attestation for a *different* `signup_id` value, `distributorId`, or `signup_reason`, exactly the class of cross-instance replay described in the report (signature reused across "contract instances" ⇒ here, signup sessions).

### Impact Explanation
The Secure Element signature is intended to attest that this specific Orb's trusted hardware root actually produced this iris/mask code at signup time — it underpins the integrity/authenticity guarantee used by the backend to trust the biometric payload. Without binding to the unique `signup_id` (or any freshness nonce), the same signed attestation can be replayed to back a different signup transaction (e.g., a different `distributorId`/operator, or a retried/duplicated signup flagged as `Fraud`/`Failure` reason), causing misattributed or duplicated signup submissions that appear hardware-attested despite not corresponding to a fresh, authorized Secure Element signing event for that transaction.

### Likelihood Explanation
Exploitation requires only observing one prior valid `(userId, codes, signature)` tuple for a given Orb/user — no admin, peer, or hardware-level access is needed, since the multipart POST fields (`userId`, `codes`, `signature`) are attacker-visible at the client layer and the signature's validity is independent of `signup_id`, `distributorId`, and `reason`. The root cause is fully within orb-core: `make_signature` simply omits available session-binding data (`signup_id`) that is already generated per attempt.

### Recommendation
Include the per-attempt `signup_id` (and ideally `distributorId`/operator id and `signup_reason`) inside the SHA-256 context signed by the Secure Element in `make_signature`, so the signature is cryptographically bound to one specific signup instance and cannot be replayed across different `signup_id`/session values. Document the exact byte layout of the signed message and add regression tests asserting that changing `signup_id` invalidates a previously captured signature.

### Proof of Concept
1. Attacker captures a legitimate signup request's multipart body (`orbId`, `distributorId`, `userId`, `codes`, `signature`) for `signup_id = A` from `src/backend/signup_post.rs::request`.
2. Attacker resubmits the identical `codes`/`signature`/`userId` payload to `POST /api/v2/signups/{B}` with a different `signup_id = B` (or a different `distributorId`).
3. Because `make_signature` in `src/plans/enroll_user.rs` never hashed `signup_id`/`distributorId` into the signed digest, the signature verifies successfully for the new signup instance `B`, letting the attacker pass off a stale Secure-Element attestation as fresh proof-of-capture for an unrelated signup session.

### Citations

**File:** wld-data-id/src/wld_data_id.rs (L54-59)
```rust
impl SignupId {
    /// Generates a globally unique signup id given the S3 region.
    #[must_use]
    pub fn new(s3_region: S3Region) -> Self {
        Self(WldDataId { version: VERSION, s3_region, signup_id: thread_rng().gen(), data_id: 0 })
    }
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
