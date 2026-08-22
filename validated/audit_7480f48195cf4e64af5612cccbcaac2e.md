I've confirmed the strongest analog in `orb-core`: the `make_signature` function in `src/plans/enroll_user.rs`, which signs iris-code signup data with the orb's secure element key but omits the `signup_id` (a per-session/per-context binding value) from the signed payload — directly analogous to the report's chainID/domain-separator omission enabling cross-context signature replay.

### Title
Missing signup-session binding in iris-code signature allows cross-signup replay of a legitimate biometric signature - (File: `src/plans/enroll_user.rs`)

### Summary
The orb signs iris-code signup data with the Secure Element private key via `make_signature` before submitting it to the backend in `signup_post::request`. Like the EIP-2612 `permit` bug, where the domain separator omits a context value (`chainID`) that can change post-deployment and enable cross-fork replay, this signature's signed payload omits `signup_id` — the value that uniquely scopes a signup transaction/session at the backend (`/api/v2/signups/{signup_id}`). Because the "context" binding the signature to one specific signup attempt is absent from the signed digest, a captured `(orbId, userId, iris codes, signature)` tuple is valid for replay into a *different* `signup_id` context, exactly as a chainID-less signature is valid across chain forks.

### Finding Description
`make_signature` in `src/plans/enroll_user.rs` builds the signed digest as: [1](#0-0) 

The hash covers `ORB_ID`, `user_qr_code.user_id`, pipeline/model versions, and the iris/mask codes for both eyes — but never the `signup_id`, which is the value that uniquely identifies the specific signup transaction at the backend endpoint: [2](#0-1) 

The `signup_id` and `signature` are sent as separate, independently-controlled fields in the multipart form to `signup_post::request`: [3](#0-2) 

`signup_id` is generated per-signup (an `orb_wld_data_id::SignupId`) and is not part of what's cryptographically bound to the signature. This mirrors the report's root cause precisely: a value that changes across contexts (chainID across forks; `signup_id` across signup sessions) is excluded from the signed schema, so the signature — proof that the orb's Secure Element actually processed this particular iris capture — is not scoped to the transaction it is meant to authorize. Because the signature is deterministic over `(orbId, userId, iris codes)` only, replaying it against a new `signup_id` (a different signup request/session for the same user) produces a signature the backend would still accept as validly signed by that orb's secure element, since nothing about the payload changed except the un-signed `signup_id` field.

### Impact Explanation
If the backend relies on this signature as proof that a genuine, fresh Secure-Element-attested iris capture occurred for a specific signup transaction (anti-fraud / liveness attestation), the missing binding to `signup_id` allows the same signed iris payload to be reused across multiple signup attempts/sessions for the same user without a new physical capture. This is a cross-signup state bleed / attestation-forgery class impact: a previously valid attestation can be misattributed to a new, unrelated signup transaction, potentially bypassing per-signup liveness/fraud enforcement that assumes each `signature` is freshly bound to its `signup_id`.

### Likelihood Explanation
Exploitability depends on whether the backend actually treats `signup_id` as part of the trust boundary the signature is meant to protect (i.e., whether it expects one signature to be usable for exactly one `signup_id`) — that backend-side verification logic is not visible in this repository. Within `orb-core`, the root cause is concretely present and reachable through the normal, unprivileged `enroll_user` signup flow that every signup goes through; no privileged orb access beyond what any signup already requires is needed to observe that the digest never varies with `signup_id`. This is a legitimate configuration weakness in the signature schema regardless of the specific backend enforcement, matching the report's own framing (a design gap that could be exploited given a suitable trigger condition, e.g., a duplicate/retried signup with the same iris data but new `signup_id`).

### Recommendation
Include `signup_id` (and ideally a freshness value/timestamp or nonce) in the data hashed by `make_signature`, so the Secure Element signature is cryptographically bound to the specific signup transaction it authorizes — analogous to including chainID in the EIP-712 signed schema instead of relying on an external, unsigned domain value. Update `make_signature` in `src/plans/enroll_user.rs` to add `ctx.update(signup_id.as_bytes())` (and validate this binding is enforced by the backend endpoint at `/api/v2/signups/{signup_id}`) before merging.

### Proof of Concept
1. Complete a normal signup for `user_id = U` on `orb_id = O`, capturing iris codes `I`, and observe the resulting `signature = S = make_signature(U, pipeline)` computed only from `(O, U, I)` per [1](#0-0) .
2. Note that `S` does not depend on `signup_id`; recomputing `make_signature` with the same `(O, U, I)` but a different `signup_id` yields the identical `S`.
3. Submit a new `signup_post::request` with a different `signup_id`, the same `signature = S`, `operator_qr_code`, `user_qr_code`, and `codes = I` per [4](#0-3) .
4. If the backend's verification only checks that `S` is a valid Secure-Element signature over `(O, U, I)` and does not separately bind `S` to the specific `signup_id` in the URL path, this request is indistinguishable from a fresh, legitimate attestation for a different signup transaction — reproducing the "signature reusable across contexts" flaw from the original chainID report.

### Citations

**File:** src/plans/enroll_user.rs (L90-102)
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
