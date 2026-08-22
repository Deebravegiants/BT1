### Title
`make_signature` omits `signup_id` (and `data_policy`/`operator_qr_code.user_id`), enabling cross-signup replay of a valid secure-element signature - (File: src/plans/enroll_user.rs)

### Finding Description
`make_signature` computes a SHA-256 digest over only `ORB_ID`, `user_qr_code.user_id`, the pipeline version strings, and the iris/mask codes for both eyes, then signs it with `secure_element::sign`. [1](#0-0) 
The `signup_id` is generated/handled separately in `Plan::run` and only passed as a plaintext path/multipart parameter to `signup_post::request`, never entering the signed digest. [2](#0-1) 
On the backend request side, `signup_id` is used only as a URL path segment (`/api/v2/signups/{signup_id}`) and the `signature` field is submitted independently in the multipart form — there is no field binding the signature to that specific `signup_id`, nor is `operator_qr_code.user_id` (`distributorId`) or any data-policy field included in the signed bytes. [3](#0-2) 

Because the digest is a deterministic function of only `(ORB_ID, user_id, ir_net_version, iris_version, iris_code, mask_code, iris_code_version)` for both eyes, two signup attempts with the same user QR code and identical captured/pipeline outputs (e.g., retry after abort with the same iris data reused, or a captured/replayed multipart body) will produce byte-identical signed digests regardless of `signup_id`. Nothing in orb-core enforces that a given signature can only be submitted under the `signup_id` it was originally computed for — that binding, if it exists at all, would have to happen entirely server-side, and the described attack path (attacker triggering two signups with the same QR code and replaying a captured multipart request) is external to the orb-core code shown and not something this file's logic prevents.

### Impact Explanation
If the backend does not independently bind `signature` to `signup_id` (which orb-core does not enforce), a signature computed for one signup session could be replayed against a different `signup_id` tied to the same `user_id`, undermining per-session attestation and potentially allowing forged/duplicated attestation of iris data across signup records. This matches an attestation-forgery / cross-signup state bleed impact category.

### Likelihood Explanation
Exploitability depends entirely on backend-side behavior that is not visible in this repository — orb-core itself does not perform any binding of the signature to signup_id, but whether the backend independently validates/binds them is unknown from the code available here. Within orb-core, the precondition (identical iris capture data reused for a retried signup with the same QR code) is plausible but requires the pipeline to produce byte-identical iris/mask codes across two capture sessions, which in practice depends on capture determinism not established in this file. This is a client-side signing gap; actual exploitability is contingent on unverified backend trust assumptions.

### Recommendation
Include `signup_id`, `operator_qr_code.user_id`, and any data-policy fields in the `make_signature` digest so the resulting signature is cryptographically bound to the specific signup session and its declared parties, preventing cross-session replay regardless of backend-side checks.

### Proof of Concept
Unit test in `src/plans/enroll_user.rs`:
1. Construct identical `qr_scan::user::Data` and `Pipeline` fixtures.
2. Call `make_signature` twice, simulating two different `signup_id` values (note: current signature does not take `signup_id` as input at all — this itself demonstrates the omission).
3. Assert the two signatures are byte-identical despite differing `signup_id`, proving the digest is signup_id-independent.
4. As a follow-up fix verification, modify `make_signature` to accept `signup_id: &str` and hash it in; re-run the test and assert signatures differ for different `signup_id` values.

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
