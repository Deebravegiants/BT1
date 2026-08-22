### Title
Secure-element iris signature is not bound to the signup session/round, enabling replay across signups - (File: `src/plans/enroll_user.rs`)

### Summary
The orb signs the captured iris codes with the secure element before submitting a signup, intended to prove that these particular iris codes were produced by this orb's hardware for this signup attempt. However, the signed payload only contains the orb ID, the user's QR-code identifier, and the iris/mask codes — it never includes the `signup_id` (the unique identifier of the specific signup round) or any timestamp/nonce. This mirrors the "Votes can be duplicated" bug class: a commitment/signature that is supposed to be tied to a specific context (voter+round in the UMA case, orb+signup-round here) is instead reusable across different rounds because the binding data was left out.

### Finding Description
`make_signature` builds the signed message as: [1](#0-0) 

It hashes `ORB_ID`, `user_qr_code.user_id`, the IR-net/iris code versions, and the left/right iris codes and mask codes, then signs the digest with the secure element:
```
ctx.update(ORB_ID...); ctx.update(user_qr_code.user_id...); ... eye_left/eye_right iris_code/mask_code ...
let signed = secure_element::sign(ctx.finish())?;
```
This signature is produced once per `Plan::run` call in `src/plans/enroll_user.rs` and is sent to the backend as a `signature` field in the multipart signup request: [2](#0-1) 

Critically, `signup_id` is used only as part of the HTTP path (`/api/v2/signups/{signup_id}`) and is passed to `signup_post::request` separately — it is never included in the data that is actually hashed and signed by the secure element: [3](#0-2) 

Because the signed digest is a deterministic function of `(orb_id, user_id, iris_code_version, iris_code, mask_code)` only, two different signup rounds (different `signup_id`s) that happen to carry the same iris codes and same user id will produce byte-identical signatures. Any code path or party able to observe/store a prior `signature` value for a given `user_id`+iris pair can resubmit it for an entirely different `signup_id` without invoking the secure element again, since nothing in the signed content ties it to a particular signup round.

### Impact Explanation
This is directly analogous to the DVM bug: the "commitment" (secure-element signature) is meant to authenticate that a genuine, fresh secure-element signing operation on this hardware backs a specific signup, but omitting the round identifier (`signup_id`) and a timestamp/nonce from the signed payload allows the same signature to be replayed/duplicated across multiple signup attempts. This can enable misattributed or duplicated signups being accepted as independently-signed events, undermining the guarantee that each signup round is uniquely and freshly attested by the orb's secure element.

### Likelihood Explanation
Exploitability depends on whether the backend cross-checks the signature payload against the current `signup_id`/round context; that server-side verification logic is out of scope for this repository, so it cannot be confirmed here. From the orb-core client code alone, nothing prevents constructing/replaying the same signature across different signup rounds because the round identifier is simply never part of what's signed — the missing binding is a concrete, provable root cause. However, actual weaponization requires either access to a previously generated `signature` value (e.g., from logs, a captured request, or client-side reuse) and would still be subject to unknown backend-side checks, which introduces some uncertainty on the full end-to-end impact.

### Recommendation
Include `signup_id` (and ideally a timestamp/nonce or PCP-equivalent) inside the data hashed by `make_signature` before it is signed by the secure element, so that the resulting signature is cryptographically bound to the specific signup round and cannot be replayed for a different `signup_id`:
```rust
ctx.update(signup_id.as_bytes());
ctx.update(timestamp.as_bytes());
```
This follows the same remediation pattern as UMA's fix (PR#1217): incorporate all relevant context (round/session id, timestamp) into the signed/committed data to prevent duplication and reuse.

### Proof of Concept
Not independently verifiable end-to-end without backend source (out of scope), but the client-side root cause is directly demonstrable by inspection:
1. Call `make_signature(user_qr_code, pipeline)` twice with the same `user_qr_code.user_id` and identical `pipeline` iris/mask codes but under two different `signup_id`s — the resulting `signature` string is identical both times because `signup_id` never enters the hashed context in `src/plans/enroll_user.rs:290-304`.
2. Submit this same `signature` value via `signup_post::request` for a second, unrelated `signup_id` (`src/backend/signup_post.rs:100-143`) — the client has no mechanism preventing this reuse, since the signed payload carries no round-binding information.

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
