### Title
Ambiguous, delimiter-free concatenation of variable-length fields before signing the iris-code signature enables field-splicing digest collisions - (File: src/plans/enroll_user.rs)

### Summary
`make_signature()` in `src/plans/enroll_user.rs` builds the digest that is signed by the Secure Element for a signup by concatenating multiple variable-length strings (`ORB_ID`, `user_id`, model/version strings, and iris/mask codes) directly into a SHA-256 context with no length-prefixing or delimiters. This mirrors the root cause of the referenced EIP-712 report: variable-length ("dynamic") fields are hashed via raw concatenation instead of a collision-resistant, unambiguous encoding, which allows different sets of field values to produce an identical signed digest.

### Finding Description
The Sherlock report's root cause is that `TitlesGraph.checkSignature()` builds `keccak256(abi.encode(ACK_TYPEHASH, edgeId, data))` by ABI-encoding a raw dynamic `bytes` value instead of first hashing it (`keccak256(data)`), which breaks EIP-712 canonicality and creates signature incompatibility issues rooted in dynamic-field-encoding ambiguity.

In orb-core, `make_signature()` builds the analogous "signed statement" for a signup as follows: [1](#0-0) 

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

Each field here is variable-length and is fed into the hash context back-to-back with no length prefix, no delimiter, and no per-field hashing — exactly the "raw concatenation of dynamic values" pattern that the EIP-712 report calls out as unsafe. Because there is no unambiguous framing between fields, two different tuples of `(user_id, ir_net_version, iris_version, iris_code, mask_code, iris_code_version, …)` can produce byte-identical concatenations (e.g., moving trailing/leading characters across an adjacent field boundary) and therefore an identical SHA-256 digest and identical Secure-Element signature. This is a lower-severity analog to the EIP-712 issue: the underlying flaw (ambiguous encoding of variable-length data prior to signing) is structurally the same, though I could not fully trace how strictly the backend validates this specific signature server-side (that verification logic lives outside this repo, in `signup_post::request` payload handling on the backend), so I cannot confirm to what degree a crafted collision would be practically exploitable end-to-end.

### Impact Explanation
If an attacker who controls some of the QR-scanned or pipeline-derived string fields (e.g. `user_id` from the scanned QR code) can shift bytes across the field boundaries used in this concatenation, they could produce a valid Secure-Element signature over a swapped/misattributed set of field values without detection, since the digest computed and verified would be identical to the digest for the legitimate set of values. This could enable cross-signup state bleed or misattribution of a signed iris-code statement to the wrong `user_id`/model versions. However, this requires attacker-influenced content in these specific fields to be crafted to produce a colliding concatenation, and I was not able to verify server-side reliance/enforcement semantics of this specific signature field beyond this repo, so the concrete blast radius is uncertain.

### Likelihood Explanation
Likelihood is low-to-moderate: `user_id` format is typically a UUID (fixed-length, limiting practical splicing opportunities) per `qr_scan::user::Data`, and the version-string fields are generally orb/pipeline-controlled rather than fully attacker-controlled, which narrows the realistic attack surface compared to the original EIP-712 report (where `data` was fully attacker/signer-controlled arbitrary bytes). Still, the coding pattern itself is a well-known "field splicing" flaw class and is not defense-in-depth safe.

### Recommendation
Use an unambiguous, collision-resistant encoding before hashing each variable-length field, e.g. hash each field independently and then hash the concatenation of fixed-length digests, or length-prefix each field before concatenation:

```rust
fn make_signature(user_qr_code: &qr_scan::user::Data, pipeline: &Pipeline) -> Result<String> {
    let mut ctx = Context::new(&SHA256);
    for field in [
        ORB_ID.as_str(),
        &user_qr_code.user_id,
        &pipeline.v2.ir_net_version,
        &pipeline.v2.iris_version,
        &pipeline.v2.eye_left.iris_code,
        &pipeline.v2.eye_left.mask_code,
        &pipeline.v2.eye_left.iris_code_version,
        &pipeline.v2.eye_right.iris_code,
        &pipeline.v2.eye_right.mask_code,
        &pipeline.v2.eye_right.iris_code_version,
    ] {
        ctx.update(&(field.len() as u64).to_be_bytes());
        ctx.update(field.as_bytes());
    }
    let signed = secure_element::sign(ctx.finish())?;
    Ok(BASE64.encode(&signed))
}
```

### Proof of Concept
Conceptually (analogous to the report's `ethers.js`/`foundry` PoC): pick two field tuples `A = (user_id="U1", ir_net_version="V")` and `B = (user_id="U", ir_net_version="1V")` such that `"U1" + "V" == "U" + "1V"` as byte strings. Feeding either tuple through `make_signature()`'s `Context::update` calls yields an identical SHA-256 digest, and thus the Secure Element produces the same signature for both, causing a signed statement over tuple A to be verified as if it were signed over tuple B, since no field-length disambiguation exists in the digest construction. I could not run this against the live backend verification path since that logic is outside this repo, so this PoC demonstrates the digest-collision root cause within orb-core only.

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
