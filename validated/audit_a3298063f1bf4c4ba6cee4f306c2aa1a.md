### Title
Secure-Element iris-code signature lacks signup-session binding (no `signup_id`/nonce/timestamp), enabling replay of a prior signed iris attestation into a different signup - ([File: src/plans/enroll_user.rs])

### Summary
The Orb signs an "iris code signature" with the Secure Element before submitting a signup, but the signed payload only covers `ORB_ID`, the scanned user's `user_id`, and the iris/mask code bytes and pipeline versions - it never includes the `signup_id`, a nonce, or a timestamp that ties the signature to a specific signup attempt. This mirrors the reported Shardus `UnjoinRequest` flaw: a validly-signed object that omits any session/replay-binding field, so a captured signature+payload pair can be resubmitted under a different transaction context and still validate.

### Finding Description
`make_signature` in `src/plans/enroll_user.rs` computes the digest that is signed by the Secure Element: [1](#0-0) 

The hashed fields are `ORB_ID`, `user_qr_code.user_id`, `pipeline.v2.ir_net_version`, `pipeline.v2.iris_version`, and the left/right iris codes, mask codes and code versions. Nothing in this digest is unique to the current signup transaction - no `signup_id`, no timestamp, no nonce.

That signature is then sent to the backend as a plain string field in the signup POST request: [2](#0-1) 

Note that `signup_id` is used only in the URL path (`/api/v2/signups/{signup_id}`) and is **not** part of the signed digest, nor is it included in the multipart form alongside the `signature` field. The calling code confirms the signature is computed once per enrollment attempt and passed through unmodified to the request: [3](#0-2) 

Because the signed material (`ORB_ID` + `user_id` + iris/mask codes + code versions) is independent of `signup_id`/session/time, any previously observed `(signature, codes, userId, orbId)` tuple for a given user remains a valid Secure-Element attestation forever and for any future signup attempt for that same user - exactly the pattern flagged in the external report: "the only thing … requested to sign is [fields with] no nonce, timestamp, or currentCycle … allowing replay."

### Impact Explanation
The Secure Element signature exists to attest that the iris code being uploaded genuinely came from this Orb's biometric pipeline for this enrollment. Since the signed digest is not bound to the specific signup transaction (`signup_id`), a previously valid `(signature, iris/mask codes)` pair for a given `userId` can be replayed into a new, unrelated signup POST (different `signup_id`, potentially different `distributorId`/operator, location, or time) and the backend has no cryptographic means, based on this field alone, to detect that the "fresh" attestation is actually a replay from an earlier (possibly rejected, fraud-flagged, or otherwise stale) signup. This is a cross-signup state bleed / attestation-forgery style issue: it undermines the integrity guarantee the signature is meant to provide across independent signup sessions.

### Likelihood Explanation
Exploitation requires an actor to obtain a previously generated `(signature, codes, userId)` triple (e.g., from logs/telemetry, a prior failed/retried signup, or interception of Orb-to-backend traffic) and resubmit it as part of a new signup request for a different `signup_id`. No cryptographic break is needed - only reuse of an already-valid signature whose scope was never restricted to a single transaction. This exactly parallels the disclosed root cause: a signed object missing anti-replay binding fields.

### Recommendation
Include the `signup_id` (and/or a timestamp/nonce) inside the digest signed by `secure_element::sign` in `make_signature`, and have the backend verify that the signed `signup_id` matches the one in the request URL. This binds each Secure-Element attestation to exactly one signup transaction and prevents replay of a previously signed iris-code attestation into a different signup context.

### Proof of Concept
As with the referenced report, the vulnerability is demonstrable by inspection of the signed structure: [1](#0-0) 

The digest hashes only `ORB_ID`, `user_qr_code.user_id`, and pipeline/iris fields - no `signup_id`, nonce, or timestamp - so the resulting signature, once produced, is valid indefinitely and independent of which signup transaction it is submitted with: [2](#0-1) 

A captured `signature` string together with the corresponding `codes`/`userId`/`orbId` fields can be resent verbatim inside a different `/api/v2/signups/{signup_id}` request, and the signed material would still validate against the Secure Element's public key, since none of it constrains which signup session it may be used in.

### Citations

**File:** src/plans/enroll_user.rs (L73-102)
```rust
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

**File:** src/backend/signup_post.rs (L125-143)
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
    let request = super::client()?
        .post(format!("{}/api/v2/signups/{signup_id}", *SIGNUP_BACKEND_URL))
        .basic_auth(&*ORB_ID, Some(get_orb_token()?))
        .multipart(form);
```
