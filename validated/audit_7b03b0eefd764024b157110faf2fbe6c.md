### Title
Secure-element iris-code signature omits signup/session context binding, enabling attestation replay across signup requests - (File: src/plans/enroll_user.rs)

### Summary
The `make_signature` function signs a hash that binds only `ORB_ID`, the user's QR `user_id`, and the iris-code payload before sending it to the backend as proof that the Secure Element attested a specific biometric capture. It never binds the signature to the specific signup session (`signup_id`), the `signup_reason`, or any other per-request context. This is structurally the same "missing domain separator" flaw as the reported LooksRareExchange bug: a signed artifact that is valid for a *class* of requests can be replayed across different request contexts because no per-context value is included in what is signed.

### Finding Description
`make_signature` in [1](#0-0)  builds the SHA-256 digest that is signed by the Secure Element from only:
- `ORB_ID`
- `user_qr_code.user_id`
- the pipeline's iris/mask codes and versions

It deliberately excludes the `signup_id`, the `signup_reason` (`Normal`/`Failure`/`Fraud`), the `s3_region`, and any timestamp/nonce, even though these are all sent alongside the signature in the same request in `signup_post::request` at [2](#0-1)  and used by the plan that calls it at [3](#0-2) .

Because the signature is computed only over the biometric payload and identifiers that don't change across retries or across attempts, the exact `(signature, codes)` pair produced by the Secure Element for one signup attempt is byte-for-byte reusable in a different backend request against a different `signup_id`, or resubmitted with the `signup_reason` field altered — the backend has no cryptographic means to detect that the signed material was generated for a different context, because that context was never part of what was signed. This mirrors the audited LooksRareExchange issue: the EIP-712 domain separator was fixed at construction and excluded a value (`chainID`) that should distinguish one execution context from another, letting a validly-signed message be replayed in an unintended context.

### Impact Explanation
The Secure Element signature is the mechanism used to attest that the iris codes uploaded during a signup truly originated from a trusted Orb capture. Because the signed digest is not bound to `signup_id` or `signup_reason`, a party in control of the multipart request body (e.g., a user/operator replaying a previously observed request) can:
- Resubmit the same signed iris-code attestation under a new `signup_id`, producing a duplicate/misattributed signup entry without a fresh, live biometric capture.
- Swap the `signup_reason` field (which is not covered by the signature) so a signup originally flagged `Fraud` is instead submitted as `Normal`, bypassing the on-orb fraud tagging while still presenting a "validly signed" biometric payload to the backend.

This falls into the concrete impact categories of misattributed signup and fraud-enforcement bypass via attestation replay.

### Likelihood Explanation
Exploitation requires the attacker to already possess one legitimately generated `(signature, iris codes)` pair for their own biometric capture (e.g., by capturing their own device's outgoing request), which is realistic for an unprivileged end user/operator abusing the normal signup flow — no privileged keys or hardware tampering are required, only observing/replaying HTTP requests that the Orb itself would otherwise send unmodified. The likelihood is moderated by network transport security (HTTPS) and by backend-side checks that are not visible in this repository, but the root cause — the signed digest's failure to bind session/context fields — is unconditionally present in the client-side code regardless of backend mitigations.

### Recommendation
Include a per-request context/domain-separation value in the signed digest, analogous to adding `chainID` to the EIP-712 domain separator in the referenced report. At minimum, add `signup_id` and `signup_reason` (and ideally a timestamp/nonce) into the `Context` update chain in `make_signature` before calling `secure_element::sign`, so that a signature cannot be replayed across a different signup session or with a modified reason without invalidating the signature.

### Proof of Concept
1. Complete a normal signup where the pipeline flags the attempt with `signup_reason = Fraud` (see `Status`/`SignupReason` usage in [4](#0-3) ). Capture the outgoing multipart POST built in [5](#0-4) , which contains `signature`, `codes`, and `reason=FRAUD`.
2. Because `make_signature` ( [1](#0-0) ) never hashed the `reason` field or `signup_id`, resend the identical `signature` and `codes` values in a new request with `reason=NORMAL` and/or a different `signup_id`.
3. Observe that the signature remains valid for the tampered request, since none of the altered fields were part of the signed digest — demonstrating the missing context/domain binding.

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
