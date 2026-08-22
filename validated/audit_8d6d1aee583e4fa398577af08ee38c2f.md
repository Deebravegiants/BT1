### Title
Iris-code attestation signature omits `signup_id`/nonce/expiry, enabling replay of stale biometric attestations across signup sessions - (File: `src/plans/enroll_user.rs`)

### Summary
The `make_signature` function that produces the secure-element-signed attestation sent to the backend during enrollment binds only `ORB_ID`, the user's QR `user_id`, and the iris pipeline output (versions, iris codes, mask codes) into the signed digest. It never includes the `signup_id`, a monotonically-increasing nonce, or an expiry timestamp, so the same signed attestation remains valid indefinitely and is not cryptographically tied to the particular signup session it is submitted with.

### Finding Description
`make_signature` builds a SHA-256 digest over a fixed set of fields and signs it with the secure element: [1](#0-0) 

The resulting `signature` is sent to the backend as a form field alongside a separately-supplied `signup_id` path parameter, but `signup_id` is never part of the signed payload: [2](#0-1) 

This mirrors the reported bug class: the signed artifact acts as an authorization/attestation token but carries no session nonce and no expiry, so it can be detached from the specific enrollment attempt (`signup_id`) it was generated for and resubmitted later, exactly as the report describes reusing stale controller signatures for a different transaction context.

### Impact Explanation
Because the signature only commits to `(ORB_ID, user_id, iris_version_strings, iris_code, mask_code)` and not to `signup_id` or a timestamp, a previously produced, backend-accepted `(signature, codes, userId)` tuple from one enrollment attempt can be resubmitted under a different `signup_id` at an arbitrary later time while still passing the same secure-element attestation check on the backend. This enables misattributed/duplicate signup submissions and cross-signup state bleed: an old iris-code capture can be presented as if freshly captured for a new signup session, undermining the freshness guarantee the attestation is meant to provide for fraud/liveness enforcement.

### Likelihood Explanation
Exploitation only requires software-level control over the HTTP request the orb-core client builds (the `signature`, `codes`, and `userId` multipart fields), reusing values captured from an earlier legitimate enrollment; no secure-element key material or physical hardware compromise is needed since the attacker replays an already-valid signature rather than forging a new one. Likelihood is bounded by the ability to intercept/replay one's own prior signup request, which is realistic for anyone operating the client software.

### Recommendation
Include `signup_id` (or a per-session nonce) and an expiry/issued-at timestamp inside the hashed payload signed by the secure element in `make_signature`, and have the backend verify both the freshness (expiry check) and binding to the specific `signup_id` before accepting the attestation, analogous to the reported fix of adding a storage-checked nonce and an `expiredAt` field to the signed inputs.

### Proof of Concept
1. Perform a normal enrollment; capture the multipart form fields sent to `POST /api/v2/signups/{signup_id}` including `signature`, `codes`, and `userId`, per `request()` in `src/backend/signup_post.rs`.
2. Start a new enrollment flow to obtain a fresh `signup_id` (generated independently of the signature payload).
3. Resend the previously captured `signature`, `codes`, and `userId` values against the new `signup_id` endpoint.
4. Because `make_signature` never included `signup_id`/nonce/expiry in the signed digest (`src/plans/enroll_user.rs:290-304`), the secure-element signature still validates, allowing the stale biometric attestation to be accepted for the new, unrelated signup session.

### Citations

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

**File:** src/backend/signup_post.rs (L100-143)
```rust
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
