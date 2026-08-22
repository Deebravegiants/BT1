### Title
Iris-code attestation signature in `make_signature` omits `signup_id`/nonce binding, enabling cross-signup replay and misattributed signup records - (File: `src/plans/enroll_user.rs`)

### Summary
The Orb signs the biometric pipeline output that is submitted to the backend signup endpoint, but the signed payload binds only to `ORB_ID` and the user's QR `user_id` plus the raw iris/mask codes — it never includes the `signup_id` (or any other session nonce) that uniquely identifies the specific signup attempt being submitted. This mirrors the H-1 root cause: a signature that authorizes/attests a sensitive action without binding to the session-specific nonce that the recipient uses to distinguish one attempt from another, allowing the signature to be validly replayed against a different session state than the one it was created for.

### Finding Description
`enroll_user::Plan::run` computes a secure-element signature over the pipeline output and sends it as the `signature` form field to `POST /api/v2/signups/{signup_id}`: [1](#0-0) 

The signed buffer is `ORB_ID || user_id || ir_net_version || iris_version || left_code || left_mask || left_code_version || right_code || right_mask || right_code_version`. Notably absent is the `signup_id` that is used as the URL path parameter for the request that carries this very signature: [2](#0-1) [3](#0-2) 

Because `signup_id` is not part of the signed data, a signature legitimately produced by the Orb's secure element for one signup attempt (same `orb_id`/`user_id`/iris output) remains cryptographically valid input for a request that names a *different* `signup_id`, `signup_reason`, `distributorId` (operator), region, or timestamp — none of which are covered by the signature either (only `orbId`, `userId`, and `codes` are signed; `signup_id`, `signup_reason`, `distributorId`, `region`, `latitude`/`longitude` are all unsigned form fields sent alongside it, per `signup_post::request`).

This is the same defect class as H-1: the signing/authorization step is decoupled from the session-identifying nonce that the verifying party (there, the liquidation facade tracking partyA/partyB nonces; here, the backend tracking `signup_id`) relies on to bind the attestation to a specific, current state. The codebase elsewhere demonstrates that the project is aware `signup_id` should be part of signed/hashed material for exactly this reason — the Personal Custody Package's `info.json` explicitly salts and hashes `signup_id` alongside `orb_id`, `operator_id`, and `timestamp`: [4](#0-3) 

`make_signature`, used for the biometric-authenticity attestation sent to the signup endpoint, was not given the same treatment.

### Impact Explanation
An attacker (an unprivileged user/operator interacting with the standard signup flow) who can capture or replay a previously-issued Orb attestation signature can pair it with a different, unsigned `signup_id`/`signup_reason`/`distributorId` combination and have the backend accept it as proof that this Orb's secure element vouches for that iris data under the new session context. This enables misattributed-signup scenarios (e.g., attaching a genuine biometric attestation to an unrelated signup session/operator/region, or reusing an attestation whose original signup outcome should not have carried over) — the same "signature valid despite session/state having changed" class of impact called out in H-1.

### Likelihood Explanation
Exploitation requires being able to observe or possess a previously issued attestation (e.g., from network capture/logging, from a prior failed/retried signup, or from control over what is submitted to the signup endpoint) and re-submit it with a different `signup_id`/metadata combination — no cryptographic break is required, only omission of the binding field, matching the "no direct crypto-primitive break" bar used for H-1.

### Recommendation
Include the `signup_id` (and ideally `signup_reason`) in the data hashed and signed by `make_signature`, so the secure-element attestation is cryptographically bound to the specific signup session it is submitted for, consistent with how `personal_custody_package.rs` already binds `signup_id` into its signed/hashed `info.json`.

### Proof of Concept
1. Inspect `make_signature` in `src/plans/enroll_user.rs:290-304`: the hashed/signed buffer is built only from `ORB_ID`, `user_qr_code.user_id`, and the pipeline's iris/mask codes and versions.
2. Inspect `signup_post::request` in `src/backend/signup_post.rs:98-143`: `signup_id` is used only as the URL path (`/api/v2/signups/{signup_id}`) and is never included in the signed buffer; `distributorId`, `region`, `reason`, `latitude`, `longitude` are likewise sent unsigned alongside the `signature` field.
3. Consequently, a signature = `Sign(ORB_ID || user_id || iris_codes)` computed for signup attempt A is bit-for-bit identical to, and thus reusable for, a request naming a different `signup_id`/`reason`/`distributorId`, since none of those values feed into the signature. This demonstrates the signature fails to bind to the specific signup session, satisfying the same root cause documented in H-1 (missing nonce/session binding in an authorizing signature).

### Citations

**File:** src/plans/enroll_user.rs (L90-101)
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

**File:** src/plans/personal_custody_package.rs (L463-493)
```rust
        let Self { credentials, signup_id, signup_reason, .. } = self;
        let Credentials { operator_qr_code, user_qr_code_string, .. } = credentials;
        let signup_id_salt = gen_salt();
        let signup_reason_salt = gen_salt();
        let orb_id_salt = gen_salt();
        let operator_id_salt = gen_salt();
        let timestamp_salt = gen_salt();
        let qr_code_salt = gen_salt();
        let orb_id = ORB_ID.as_str();
        let timestamp = self
            .capture_start
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
            .to_string();
        let orb_public_key_certificate = BASE64.encode(&ORB_PUBLIC_KEY);
        let left_ir_image_id = self.identification_image_ids.left_ir.to_string();
        let right_ir_image_id = self.identification_image_ids.right_ir.to_string();
        let thumbnail_image_id = self.identification_image_ids.self_custody_candidate.to_string();
        let software_version = &**ORB_OS_VERSION;
        let orb_country = self.location_data.operator_team_operating_country.clone();
        hashes.insert("signup_id".to_owned(), salted_sha256(signup_id, &signup_id_salt));
        hashes
            .insert("signup_reason".to_owned(), salted_sha256(signup_reason, &signup_reason_salt));
        hashes.insert("orb_id".to_owned(), salted_sha256(orb_id, &orb_id_salt));
        hashes.insert(
            "operator_id".to_owned(),
            salted_sha256(&operator_qr_code.user_id, &operator_id_salt),
        );
        hashes.insert("timestamp".to_owned(), salted_sha256(&timestamp, &timestamp_salt));
        hashes.insert("qr_code".to_owned(), salted_sha256(user_qr_code_string, &qr_code_salt));
```
