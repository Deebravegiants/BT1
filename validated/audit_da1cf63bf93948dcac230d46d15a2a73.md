### Title
Iris-code signature computed by `make_signature` does not bind `signup_id` or `distributorId`, allowing cross-signup / cross-operator misattribution - (File: `src/plans/enroll_user.rs`)

### Summary
The `_invalidateOrderNonce`-style bug in the external report is about a signature/nonce that omits the party it is meant to protect, letting an unrelated actor "own" the nonce. The closest analog in `orb-core` is `make_signature()` in `src/plans/enroll_user.rs`, which is the secure-element attestation that is supposed to cryptographically bind a specific iris capture to a specific signup. That signature hashes only `ORB_ID`, `user_qr_code.user_id`, and the iris pipeline outputs — it never includes the per-request `signup_id` or the operator/`distributorId` that are sent alongside it in the same multipart form to the backend.

### Finding Description
`make_signature` builds the signed payload as: [1](#0-0) 

This is the only cryptographic attestation tying the biometric templates to an actual signup transaction; it is produced with the orb's private key via `secure_element::sign`: [2](#0-1) 

The signed digest omits two fields that are transmitted in the very same request and that the backend uses to determine *which session* and *which operator/distributor* the signup is credited to: [3](#0-2) 

Specifically:
- `signup_id` is only used as a URL path segment (`/api/v2/signups/{signup_id}`) and is never part of the signed digest.
- `distributorId` (derived from `operator_qr_code.user_id`) is included as a plain form field but is likewise absent from the signature.

Because the signature only binds `ORB_ID + userId + iris codes/versions`, the backend cannot cryptographically verify that this particular signed attestation was produced for *this* `signup_id` or *this* `distributorId`. The signature is therefore reusable across different `signup_id`/`distributorId` values without invalidating it — structurally the same flaw as the reported bug, where `_invalidateOrderNonce` sets a nonce for `_trader` without that trader's signature ever being part of the signed order, so the binding between the protected party and the signed artifact is missing.

### Impact Explanation
If the `signature`, `codes`, and `userId` fields of a previously valid signup request are replayed with a different `signup_id` and/or `distributorId` (e.g., due to retry logic, backend replay, or any component/path that reconstructs the multipart form independently of the original request), the backend has no cryptographic means to detect that the attestation was not actually produced for that specific session or operator. This can lead to:
- Misattribution of a signup to a different operator/distributor than the one who actually performed it.
- Cross-signup state bleed: a signed capture intended for one signup transaction accepted under a different `signup_id`.

This matches the "misattributed signup" and "cross-signup state bleed" impact categories called out as valid in the prompt's validation criteria.

### Likelihood Explanation
Exploitability depends entirely on whether any reachable code path can present the signed triple (`signature`, `userId`, `codes`) together with an attacker-influenced `signup_id`/`distributorId` — e.g., through retried/duplicated requests, or backend-side reconciliation issues. I was not able to fully verify from `orb-core` alone whether the backend independently re-derives/checks `signup_id` and `distributorId` against some other server-side session record that would prevent this from being exploitable in practice; that server-side validation logic lives outside this repository and outside the index I could search. The `orb-core` side, however, definitively does not include these fields in the signed digest, so the client-side control that could prevent misuse is absent by design — the same root cause pattern as the reported bug (protecting party's identity omitted from the signed data).

### Recommendation
Include `signup_id` and `distributorId` (operator identity) inside the digest signed in `make_signature`, so the secure-element signature cryptographically commits to the specific signup session and the specific operator/distributor, mirroring the report's recommendation to include the trader's identity/signature in the signed nonce data. Concretely, update: [4](#0-3) 

to also `ctx.update()` the `signup_id` and `operator_qr_code.user_id` before signing, and update `signup_post::request` to pass those values into the signature computation call site so the backend can validate that the signature matches the session and operator being submitted.

### Proof of Concept
Conceptual (not independently executed, since I only had static index access to this repo, not a live backend or the ability to run/replay HTTP requests):
1. Capture a legitimate signup's `signature`, `userId`, and `codes` form fields for `signup_id = S1`, `distributorId = D1`.
2. Resubmit the identical `signature`/`userId`/`codes` values to `/api/v2/signups/{S2}` with `distributorId = D2`.
3. Because `make_signature` never included `S1`/`D1` in the signed digest, the signature remains valid for the new `(S2, D2)` combination from the orb-core client's perspective — the backend's ability to reject this depends solely on server-side logic not present in this repository, which I could not verify.

**Uncertainty note:** I could not confirm from the `orb-core` codebase alone whether backend-side controls (outside this repo) already prevent replay/misattribution via other means (e.g., single-use `signup_id` tokens tied server-side to the request). This finding is scoped strictly to the client-side signature construction, which structurally mirrors the reported vulnerability's root cause (signed data omitting the identity/session it is meant to protect).

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

**File:** src/backend/signup_post.rs (L98-133)
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
```
