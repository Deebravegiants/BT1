### Title
Missing session/transaction binding in secure-element signup signature enables signature replay across signup attempts - (File: src/plans/enroll_user.rs)

### Summary
The external report describes an `ERC20Permit`-style bug where a signed message omits a domain separator (`chainID`), letting a signature computed for one context be replayed in another. The closest reachable analog in `orb-core` is `make_signature` in `src/plans/enroll_user.rs`, which builds the payload signed by the secure element for a signup without including the `signup_id` (the per-attempt transaction identifier) that ties the request together on the backend side.

### Finding Description
`make_signature` hashes `ORB_ID`, the user QR `user_id`, pipeline/iris versions, and the iris/mask codes, then signs the digest via `secure_element::sign` [1](#0-0) . This signature and the raw iris/mask codes are later submitted together with a separate, unsigned `signup_id` path parameter and `userId`/`orbId` form fields to the backend via `signup_post::request` [2](#0-1) . Because `signup_id` (the value that scopes a request to one specific signup transaction, analogous to `chainID` scoping a permit to one specific chain) is never part of the signed digest, the signature only attests to `(orb, user, iris codes)`, not to *which* signup attempt it belongs to. This mirrors the `ERC20Permit` flaw: the signed artifact is not bound to the transactional context it is meant to authorize, so if the same signed artifact can reach the backend under a different `signup_id`, the backend cannot distinguish a legitimate submission from a replayed one purely from the signature.

### Impact Explanation
If a previously valid `(signature, codes)` pair for a given orb/user could be resubmitted against a different `signup_id`, it would let a party misattribute a biometric enrollment result to a different signup event without the orb ever re-running the biometric/liveness pipeline for that event — a cross-signup state bleed / misattributed-signup scenario. This is analogous to the reported theft-via-replay pattern, but for signup attestation rather than token allowance.

### Likelihood Explanation
This is a real code-level gap (no domain separation for the signed data), but I could not fully verify the exploitability boundary from the client repo alone: the request is sent over TLS with orb-token basic auth (`get_orb_token()`) [3](#0-2) , and backend-side replay/duplicate detection (which is out of scope for this repo) may already reject a signature tied to a different/previous `signup_id`. I was not able to confirm within `orb-core` whether any component ever reuses a captured `Pipeline`/`Capture` across two distinct `signup_id`s (which would make this trivially triggerable), nor could I inspect backend verification logic to confirm the signature is actually checked for `signup_id` binding. Given these unknowns, likelihood should be treated as unconfirmed rather than proven.

### Recommendation
Include `signup_id` (and ideally a monotonic/unique nonce or timestamp) in the data hashed by `make_signature` before signing, so the secure-element signature is cryptographically bound to the specific signup transaction it accompanies, mirroring the "include `chainID`" recommendation from the source report.

### Proof of Concept
Not independently reproducible from the `orb-core` repo alone — the concrete replay would require either (a) a component that resubmits a previously computed `(signature, codes)` pair under a new `signup_id`, or (b) backend-side confirmation that `signup_id` is not cross-checked against the signature. Neither could be verified with the tools/scope available here, so this should be treated as a code-pattern flag requiring backend-side confirmation before being scored as a proven vulnerability.

### Citations

**File:** src/plans/enroll_user.rs (L290-303)
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
