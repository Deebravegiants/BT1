### Title
Iris-code signature omits `signup_id` and operator/distributor identity, enabling cross-signup misattribution - (File: `src/plans/enroll_user.rs`)

### Summary
The signature that `orb-core` computes over a user's iris codes before submitting a signup is not bound to the specific signup session (`signup_id`) or to the operator/distributor identity (`distributorId`), even though both values are transmitted alongside the signature in the same request. This mirrors the reported `MoonscapeDefi.stakeToken` flaw, where a signature was accepted without binding it to the actual caller/context, allowing the signed payload to be paired with a different, unauthorized context.

### Finding Description
`make_signature` in `src/plans/enroll_user.rs` computes the signed digest only from `ORB_ID`, the user's QR `user_id`, and the iris pipeline codes/versions: [1](#0-0) 

This signature (produced by the Secure Element, see `secure_element::sign` at [2](#0-1) ) is then submitted to the backend as a separate `signature` form field, alongside `signup_id`, `distributorId` (from `operator_qr_code.user_id`), and `userId`: [3](#0-2) 

Because `signup_id` and `distributorId` are not part of the signed message, the cryptographic guarantee provided by the Secure Element only proves "this Orb captured these iris codes for this `user_id`" — it does not prove which signup session or which operator/distributor the capture belongs to. Any component or actor able to construct/replay this multipart request (e.g. by resubmitting a previously captured signature with a different `signup_id` or `distributorId` field) can misattribute a valid, signed biometric capture to a different signup session or a different operator/distributor without invalidating the signature, exactly as the reported bug describes a signature that isn't bound to the actual authorized party (`msg.sender`).

### Impact Explanation
A successfully signed iris-code payload can be resubmitted under a different `signup_id` or a different `distributorId`, since neither value invalidates the existing Secure-Element signature. This can lead to cross-signup misattribution of a genuine biometric capture (attributing a signup to the wrong operator/distributor, or replaying a signed capture into an unrelated signup session), which is a direct analog to the "stake on behalf of another user" misattribution impact in the original report.

### Likelihood Explanation
The `signup_id` and `distributorId` values are always sent as plain, unsigned form fields alongside the signature on every signup (`src/backend/signup_post.rs` lines 125-143), and the vulnerable signing logic (`make_signature`) runs on every signup where a `pipeline` is present. No special conditions are needed beyond control over the fields transmitted in this request, other than the signed iris codes/version fields themselves, which are unrelated to the session/operator binding.

### Recommendation
Include `signup_id` and the operator/distributor identifier (`operator_qr_code.user_id`) in the data hashed and signed by `make_signature`, so that the Secure Element signature cryptographically binds the iris-code capture to the specific signup session and operator it was captured for, preventing reattribution to a different session/operator.

### Proof of Concept
1. Perform a normal signup; capture the resulting `signature` value computed in `make_signature` and the associated iris `codes`.
2. Resubmit `signup_post::request` with the same `signature` and `codes`, but a different `signup_id` and/or `distributorId`.
3. Because these fields are not part of the signed digest, the signature remains valid for the backend's verification (which only re-derives the digest from `ORB_ID`, `user_id`, and iris codes), allowing the biometric capture to be attributed to a different signup session/operator than the one it was actually captured under.

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

**File:** src/secure_element.rs (L10-47)
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

        let mut stdin = child.stdin.take().unwrap();
        stdin.write_all(encoded.as_bytes())?;
        drop(stdin);

        let output = child.wait_with_output().wrap_err("waiting for orb-sign-iris-code")?;
        let success = output.status.success();
        for line in String::from_utf8_lossy(&output.stderr).lines() {
            if success {
                tracing::trace!("orb-sign-iris-code {}", line);
            } else {
                tracing::error!("orb-sign-iris-code {}", line);
            }
        }
        if !success {
            if let Some(code) = output.status.code() {
                bail!("orb-sign-iris-code exited with non-zero exit code: {code}");
            } else {
                bail!("orb-sign-iris-code terminated by signal");
            }
        }
        BASE64.decode(&output.stdout).wrap_err("decoding orb-sign-iris-code output")
    }

    inner(data.as_ref())
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
