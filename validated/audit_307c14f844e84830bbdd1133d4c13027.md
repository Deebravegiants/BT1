### Title
Signup signature (`make_signature`) excludes `distributorId` and `signup_reason` from the signed payload, allowing tampering with operator attribution and fraud classification - (File: `src/plans/enroll_user.rs`)

### Summary
`make_signature` in `src/plans/enroll_user.rs` computes a SHA256-based signature that is sent to the backend as proof that the iris data in the signup request was produced by this Orb for this user. Like the `CalculateRequestHash` bug in the external report (which hashes everything except `QuorumIDs`, allowing an intercepted request's `QuorumIDs` to be swapped without invalidating the hash), this signature covers only a subset of the fields that are actually transmitted in the same request. Fields such as the operator/distributor identity and the signup reason are sent alongside the signature but are not included in what is hashed and signed, so they can be altered post-signature without detection.

### Finding Description
`make_signature` builds the signed digest from only these fields: [1](#0-0) 

Specifically it hashes `ORB_ID`, `user_qr_code.user_id`, and the pipeline's iris/mask codes and versions — nothing else.

That signature is then sent as one field (`signature`) inside a multipart form built by `signup_post::request`, alongside several other fields that are **not** covered by the hash: [2](#0-1) 

In particular:
- `distributorId` (`operator_qr_code.user_id`) — identifies which operator/distributor gets credit for the signup — is sent but never hashed.
- `reason` (`signup_reason`, e.g. `NORMAL`/`FAILURE`/`FRAUD`) — is sent but never hashed.
- `region`, `latitude`, `longitude` are likewise excluded from the signed data.

Because the backend's only cryptographic assurance over this request is this signature, and the signature's coverage does not include `distributorId` or `reason`, those two fields are effectively unauthenticated: they can be modified after the Orb produces the signed payload (e.g. by a party intercepting or replaying the request) without causing signature verification to fail, exactly the same bug class as `CalculateRequestHash` omitting `QuorumIDs`.

### Impact Explanation
- Tampering with `distributorId` without invalidating the signature enables a misattributed signup: a legitimate, correctly-signed iris signup could be re-attributed to a different operator/distributor than the one who actually performed it.
- Tampering with `signup_reason` without invalidating the signature allows a signup that the Orb flagged as `Fraud` to be resubmitted/altered as `Normal` (or vice versa), undermining the backend's fraud/liveness bookkeeping for that signup, since the reason field is exactly the channel orb-core uses to tell the backend "this was a fraud attempt at the orb."

### Likelihood Explanation
The signature is the sole binding mechanism validating this request's biometric payload; the request is built and transmitted by `signup_post::request` as a standard multipart HTTP form, and any component capable of modifying the outgoing form data before/during transmission (or replaying a captured request with edited fields) can change `distributorId` or `reason` while keeping the same, still-valid `signature` field, since that signature never covered those bytes in the first place.

### Recommendation
Include all security-relevant fields that are transmitted with the request — at minimum `distributorId` (operator/distributor id) and `signup_reason` — in the data hashed by `make_signature`, so any modification of these fields invalidates the signature, matching the fix recommended for `CalculateRequestHash` (include `QuorumIDs` in the hash).

### Proof of Concept
1. Orb-core computes `signature` via `make_signature`, which only covers `ORB_ID`, `user_qr_code.user_id`, and iris/mask codes/versions: [1](#0-0) 
2. `signup_post::request` builds the multipart form including `distributorId` and `reason` fields separately from, and not covered by, that `signature`: [3](#0-2) 
3. An attacker able to intercept/modify the outgoing request can change the `distributorId` or `reason` field values while leaving `signature` unchanged; because `make_signature` never included these fields, the backend's signature check (which only validates the hashed subset) cannot detect the tampering, resulting in a misattributed signup or an altered fraud classification for that signup.

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

**File:** src/backend/signup_post.rs (L125-139)
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
```
