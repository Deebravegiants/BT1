### Title
Signup Signature Omits Operator Attribution and Fraud-Reason Fields, Enabling Signup Misattribution and Fraud-Flag Tampering - (File: src/plans/enroll_user.rs)

### Summary
`make_signature` in `src/plans/enroll_user.rs` computes a cryptographic signature over only a subset of the fields that are transmitted to the signup backend. Fields such as the operator's identifier (`distributorId`) and the fraud/failure `reason` classification are sent alongside the signed payload in `signup_post::request`, but they are never included in the data that gets hashed and signed. This is the same class of defect as the reported `Permit2OrderLib` issue: values present in the transmitted "witness"/payload are not represented in the signed typed structure, so the signature fails to guarantee the integrity of the full message.

### Finding Description
`make_signature` builds a SHA-256 digest and signs it with the Secure Element, but only over: `ORB_ID`, `user_qr_code.user_id`, `pipeline.v2.ir_net_version`, `pipeline.v2.iris_version`, and the iris code/mask/version for both eyes. [1](#0-0) 

The resulting signature is then sent to the backend as one field of a much larger multipart form built in `signup_post::request`, which also includes `distributorId` (the operator's QR code user ID), `region`, `reason` (the `SignupReason`: `Normal`/`Failure`/`Fraud`), and optional `latitude`/`longitude` — none of which are part of the signed digest. [2](#0-1) 

The `SignupReason` enum explicitly encodes whether the Orb itself flagged the signup as fraudulent, and this value is serialized directly into the unsigned `reason` form field. [3](#0-2) 

Because the signature is meant to let the backend cryptographically verify that the biometric payload legitimately originated from this Orb's Secure Element, any field left outside the hash provides no such guarantee. The `distributorId` (operator identity) and `reason` (Orb-side fraud/failure classification) are exactly the kind of security-relevant metadata that should be bound to the signature — analogous to how `Permit2OrderLib`'s `witnessTypeString` must include every field present in the signed witness struct to prevent inconsistency between what is cryptographically committed to and what is actually transmitted.

### Impact Explanation
- **Misattributed signup**: `distributorId` (the operator identifier) is not covered by the signature, so it can be altered on the wire (e.g. by a compromised transport intermediary or component between signature generation and the HTTP request) without invalidating the Secure-Element-backed signature, letting a signup be attributed to the wrong operator.
- **Fraud-flag bypass**: the `reason` field (`Normal`/`Failure`/`Fraud`) is likewise unsigned. An Orb-side fraud detection result can be silently downgraded from `Fraud`/`Failure` to `Normal` in transit without breaking the signature check, undermining the backend's ability to trust the Orb's own fraud signal.

### Likelihood Explanation
Exploitation requires the ability to modify the outbound signup request after `make_signature` runs but before/while it is transmitted (e.g., a compromised component on the request path, or a break in transport integrity assumptions). This is a narrower window than a fully remote attacker, but it defeats the entire purpose of having a Secure-Element signature as a defense-in-depth integrity check independent of TLS — the signature currently protects only the biometric code fields and silently excludes operator- and fraud-relevant metadata that travels in the same request.

### Recommendation
Include all security-relevant fields that are transmitted alongside the signature — at minimum `distributorId` (or the operator's user ID) and `signup_reason` — in the data hashed by `make_signature`, so that the Secure Element signature attests to the full set of fields the backend relies on, not just the iris code data. Any field sent in the multipart form in `signup_post::request` that affects signup attribution or fraud handling should be part of the signed digest.

### Proof of Concept
1. Orb runs the enrollment plan; `make_signature` hashes/signs only `ORB_ID + user_qr_code.user_id + ir_net_version + iris_version + iris codes/masks` (`src/plans/enroll_user.rs:290-304`).
2. `signup_post::request` builds the multipart form including the unsigned `distributorId` and `reason` fields alongside the signature (`src/backend/signup_post.rs:125-133`).
3. An entity able to intercept/modify the outbound request between signature computation and transmission changes `reason` from `FRAUD` to `NORMAL`, or swaps `distributorId` to a different operator's ID.
4. The backend, verifying only the signature over the originally-hashed fields, cannot detect this tampering because `reason` and `distributorId` were never part of the signed digest — resulting in a fraud-flagged signup being accepted as normal, or a signup being misattributed to a different operator.

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

**File:** src/backend/signup_post.rs (L72-82)
```rust
/// Every signup needs to be tagged with a reason for the backend to process it.
#[derive(Serialize, Debug, Default, Copy, Clone, PartialEq, Eq)]
pub enum SignupReason {
    /// Signup was successfully processed on the Orb.
    #[default]
    Normal,
    /// Signup failed due to some agent dying in the biometric pipeline or some internal error.
    Failure,
    /// Signup was detected as a fraud attempt at the orb (not to be confused with the backend fraud checks).
    Fraud,
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
