### Title
`make_signature` does not bind the signature to `signup_id`, allowing the same attestation to be reused across different signup sessions - (File: `src/plans/enroll_user.rs`)

### Summary
`make_signature` computes a SHA256 context over `ORB_ID`, `user_qr_code.user_id`, and the pipeline's iris/mask codes, then signs it with `secure_element::sign()`. The `signup_id` (the per-session transaction identifier used in the backend URL `/api/v2/signups/{signup_id}`) is never mixed into the signed digest, so the resulting attestation is a function only of `(orb_id, user_id, iris_codes)` and is identical for any two signup sessions that share those inputs.

### Finding Description
`make_signature` in `src/plans/enroll_user.rs` builds the signed digest as: [1](#0-0) 
None of the hashed fields include `self.signup_id`. The `signup_id` is only used later, as a path segment and separate multipart form value, when POSTing to the backend: [2](#0-1) 
Because the signature and the `signup_id` travel to the backend as two independent, unlinked values (`signature` text field vs. the URL path `{signup_id}`), the cryptographic attestation produced by the secure element does not itself prove which signup transaction it belongs to. Any code path (client-side replay, MITM within an attacker's own session, or backend logic bug) that pairs a previously produced `signature` with a different `signup_id` for the same `orb_id`/`user_id`/iris-code triple would be accepted as a self-consistent attestation from the client's perspective, since orb-core never re-derives or checks the binding of signature to signup_id.

### Impact Explanation
This weakens the intended security property that the secure-element-backed attestation proves an orb-specific, session-specific act of biometric capture for a given `signup_id`. If backend-side verification does not independently and cryptographically bind `signature` to `signup_id` (this repo only shows the client sending both as separate fields; server-side enforcement is outside this repo's visibility), a captured `signature` could be replayed for a different signup transaction with the same `user_id`/iris output, i.e. attestation forgery / replay across signups.

### Likelihood Explanation
Exploitability is bounded by real-world constraints not fully verifiable from this repo alone: (1) iris/mask codes are derived from live biometric capture and are unlikely to be bit-identical across two separate optical captures due to sensor noise, so naturally producing two sessions with byte-identical `pipeline.v2` fields may be hard without directly reusing captured artifacts; (2) whether the backend independently binds `signature` to `signup_id` server-side is unknown from this codebase. Given these unknowns, likelihood is moderate-to-low but the root cause (missing binding) is a concrete design gap, not backend behavior we can confirm mitigates it.

### Recommendation
Include `signup_id` (or an equivalent freshness/session nonce) as one of the fields hashed inside `make_signature`'s `Context`, e.g. `ctx.update(signup_id.as_bytes())`, before calling `secure_element::sign()`. This cryptographically binds the attestation to the specific signup transaction and prevents replay of a valid signature across different `signup_id`s.

### Proof of Concept
Unit test in `src/plans/enroll_user.rs`:
1. Construct two `Pipeline` objects with identical `ir_net_version`, `iris_version`, and identical `eye_left`/`eye_right` `iris_code`/`mask_code`/`iris_code_version` values (simulating an attacker replaying the same biometric output).
2. Construct two `qr_scan::user::Data` values with the same `user_id`.
3. Call `make_signature(&user_qr_code, &pipeline)` for both — assert the outputs are equal even though the two calls are meant to represent two distinct `signup_id` sessions, i.e., `make_signature` never takes `signup_id` as input at all.
4. Add an invariant assertion: expect `make_signature`'s signature to differ when only `signup_id` differs (currently impossible to write meaningfully because the function signature has no `signup_id` parameter) — this absence itself demonstrates the missing binding.

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
