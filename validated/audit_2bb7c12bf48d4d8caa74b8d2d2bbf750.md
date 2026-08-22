### Title
Signup enrollment signature is not bound to the per-signup nonce, enabling replay of a stale iris-signature across distinct signup submissions - (File: `src/plans/enroll_user.rs`)

### Summary
`enroll_user::Plan::run` computes an ECDSA signature over the enrollment payload via `make_signature`, which is signed by the Secure Element and sent to the backend along with a freshly-generated, random `SignupId` to authenticate the enrollment. However, the signed digest only covers `ORB_ID`, `user_qr_code.user_id`, and the deterministic biometric pipeline outputs (iris/mask codes and model versions) — it never incorporates the unique, randomly generated `signup_id` (or any other single-use nonce/timestamp) that is supposed to bind the signature to one specific signup transaction. This mirrors the Biconomy paymaster bug class: an authorization artifact meant to authorize a single operation is computed independently of the value (nonce/id) that should make it unique per operation, so the same signature can be legitimately replayed against a different transaction identifier.

### Finding Description
`SignupId::new` generates a fresh random 10-byte nonce per signup attempt: [1](#0-0) 
and this ID is used as the URL path parameter (`/api/v2/signups/{signup_id}`) that scopes each backend signup submission: [2](#0-1) 

The cryptographic proof-of-capture (`signature`) submitted in that same request is computed by `make_signature`: [3](#0-2) 
As shown, the digest hashes only `ORB_ID`, `user_qr_code.user_id`, pipeline/model version strings, and the iris/mask codes produced by the biometric pipeline — it does **not** hash `signup_id`, a timestamp, or `signup_reason`. All of these inputs are deterministic outputs of a single biometric capture for a given user, meaning the exact same signature bytes can be reproduced/replayed for that user's biometric data regardless of which `signup_id` the request is submitted under.

The signature is generated once per enrollment attempt in `Plan::run` and then submitted with the corresponding `signup_id`: [4](#0-3) 
Because the signature has no cryptographic binding to `signup_id`, an attacker with access to a previously-produced valid signature and the corresponding iris/mask code payload (e.g. captured/logged locally, or replayed by any code path with access to `signup_post::request`, which is a plain public async function taking `signature`, `signup_id`, `capture`, `pipeline`, and `signup_reason` as independent parameters) can submit the same signature for a new, distinct `signup_id`.

This is compounded by the fact that local fraud detection in this build is fully disabled: [5](#0-4) 
so the Secure Element signature is effectively the sole cryptographic assurance that a given enrollment corresponds to a genuine, single biometric capture event; nothing in the orb-core client enforces that the signature is single-use or bound to the signup context before it is handed to the backend.

### Impact Explanation
If the backend's anti-fraud/anti-duplicate logic relies on the Orb-issued signature as proof that a specific `signup_id` corresponds to a genuine, distinct capture (the standard purpose of Orb-signed enrollment payloads), the missing binding allows the same signed payload to be attributed to multiple different signup IDs. This can result in unauthorized/misattributed signups being accepted as legitimate, duplicate world-ID credentials being issued from a single biometric capture, or the local fraud/liveness gate's absence being unmasked as the only defense, since the signature itself carries no protection against reuse across different signup contexts. This falls squarely into the "unauthorized/misattributed signup" and "fraud/liveness bypass" impact categories.

### Likelihood Explanation
The precondition is realistic for the baseline "malicious normal user / malicious client" threat model: anyone able to capture or intercept one legitimate signature+iris-code payload (e.g., from local logs, debug output, or a modified/rooted orb client) can invoke `signup_post::request` (a plain public function, not gated by any additional per-call secret) with a new `signup_id` and the old signature. No privileged keys, hardware tampering, or breaking of the underlying ECDSA primitive is required — only reuse of already-valid signed data across a different logical transaction, which is exactly the missing-nonce-binding root cause identified in the paymaster analog.

### Recommendation
Bind the Secure-Element signature to the unique, single-use `signup_id` (and ideally `signup_reason`) by including it in the hashed payload in `make_signature`, e.g.:
```rust
fn make_signature(user_qr_code: &qr_scan::user::Data, pipeline: &Pipeline, signup_id: &str) -> Result<String> {
    let mut ctx = Context::new(&SHA256);
    ctx.update(ORB_ID.as_str().as_bytes());
    ctx.update(signup_id.as_bytes());
    ctx.update(user_qr_code.user_id.as_bytes());
    // ... existing fields
}
```
and update `enroll_user::Plan::run` to pass `signup_id` into `make_signature` before signing, ensuring the signature is cryptographically single-use per signup.

### Proof of Concept
1. On a rooted/modified Orb (or a captured HTTP request log), obtain a previously valid `(signature, iris_code, mask_code, user_id)` tuple produced by `make_signature` in `src/plans/enroll_user.rs` for a completed signup.
2. Call `signup_post::request` (`src/backend/signup_post.rs`) directly with the same `signature`, `capture`, and `pipeline`, but a new, freshly-generated `signup_id` (`SignupId::new`, `wld-data-id/src/wld_data_id.rs`).
3. Because `make_signature` never included `signup_id` in the signed digest, the exact same signature bytes remain valid for the new request, which the backend cannot distinguish from a fresh, genuine capture using only the signature.

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

**File:** src/backend/signup_post.rs (L140-143)
```rust
    let request = super::client()?
        .post(format!("{}/api/v2/signups/{signup_id}", *SIGNUP_BACKEND_URL))
        .basic_auth(&*ORB_ID, Some(get_orb_token()?))
        .multipart(form);
```

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

**File:** src/plans/mod.rs (L1390-1406)
```rust
    /// Performs the fraud checks.
    #[allow(clippy::too_many_lines)]
    async fn detect_fraud(
        &mut self,
        orb: &mut Orb,
        _debug_report: &mut debug_report::Builder,
        pipeline: Option<&biometric_pipeline::Pipeline>,
    ) -> Result<bool> {
        orb.set_phase("Fraud detection").await;
        let Some(_pipeline) = pipeline else {
            return Ok(false);
        };

        // FOSS: WE HAVE DELETED ALL FRAUD CHECKS

        Ok(false)
    }
```
