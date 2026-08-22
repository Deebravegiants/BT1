## Title
Ignored deletion result in `finalize_signup` may leave biometric identification images retained on disk - (File: src/agents/image_notary.rs)

### Summary
The external report flags a pattern where a fallible operation's result value is discarded, allowing an operation to silently fail without the caller (or system) noticing. The closest analog in `orb-core` is in the `image_notary` agent's `finalize_signup` function, where the result of `ssd::perform` — which attempts to delete the per-signup save directory containing identification images — is discarded instead of being checked or propagated as an error.

### Finding Description
In `src/agents/image_notary.rs`, the `finalize_signup` method (compiled when the `internal-data-acquisition` feature is disabled) is defined as: [1](#0-0) 

```rust
#[cfg(not(feature = "internal-data-acquisition"))]
#[allow(clippy::unnecessary_wraps)]
fn finalize_signup(&mut self) -> Result<()> {
    // In theory this is not needed. Just an extra defensive measure.
    ssd::perform(|| {
        self.save_dir.exists().then(|| remove_dir_all(&self.save_dir)).unwrap_or(Ok(()))
    });
    Ok(())
}
```

The call to `ssd::perform(...)` — which wraps the removal of `self.save_dir` (the per-signup directory that stores identification images and other captured biometric artifacts, per `save_identification_images_impl` and related handlers earlier in the same file) — has its return value completely discarded. The function then unconditionally returns `Ok(())`, regardless of whether the directory removal actually succeeded. This mirrors the reported bug class: a fallible operation's result is ignored, so failure is silently swallowed and the caller/broker believes the operation succeeded (`Ok(())` is always returned) even though the underlying cleanup may not have happened.

This is invoked from the agent's main event loop on `Input::FinalizeSignup`: [2](#0-1) 

### Impact Explanation
`self.save_dir` holds identification images and other saved biometric capture data tied to a specific `signup_id` [3](#0-2) . If the underlying `remove_dir_all` call fails (e.g., due to an I/O error, filesystem corruption, or SSD write-protection state), `ssd::perform` presumably reports that failure, but `finalize_signup` never inspects it — the return is discarded and `Ok(())` is returned regardless. As a result:
- The Orb's broker/plan logic proceeds under the assumption that signup data was properly finalized/cleaned up.
- Leftover biometric identification image files for a completed signup could remain on disk beyond their intended retention window, which is a data-retention concern for biometric data as flagged in the "biometric upload and retention" category.

This is a lower-severity issue than the original report's fund-transfer scenario, since it does not cause fund loss, but it is a legitimate ignored-result-value analog with a plausible data-retention impact.

### Likelihood Explanation
The failure path depends on an underlying filesystem/SSD failure during `remove_dir_all`, which is not attacker-controlled and would typically only occur under abnormal storage conditions (already-documented as a known failure mode elsewhere in this same file, e.g. `ensure_enough_space` and other `ssd::perform` guarded calls). This makes the likelihood of exploitation low and mostly triggered by hardware/storage faults rather than a directly reachable, unprivileged-user-triggerable attack path. I was not able to fully verify the internals of `ssd::perform`'s return type/semantics (attempts to read `src/ssd.rs` did not complete due to tool errors in the final iteration), so the exact failure semantics (e.g., whether it logs internally, retries, or truly swallows errors silently) remain unconfirmed.

### Recommendation
Propagate or explicitly log the result of `ssd::perform` in `finalize_signup` rather than discarding it, e.g.:
```rust
fn finalize_signup(&mut self) -> Result<()> {
    ssd::perform(|| {
        self.save_dir.exists().then(|| remove_dir_all(&self.save_dir)).unwrap_or(Ok(()))
    })
    .wrap_err("failed to remove signup save directory during finalize_signup")?;
    Ok(())
}
```
This ensures that failures to clean up biometric identification images are surfaced (e.g., via `tracing::error!` and/or a Datadog counter) rather than being silently ignored, consistent with how other failure paths in the same file already log and count errors (e.g., `handle_save_identification_images`, lines 394-399 of the same file).

### Proof of Concept
Not applicable as an externally-triggerable PoC — this is a code-inspection finding based on ignored return value semantics rather than an unprivileged-user-reachable exploit chain. I could not confirm at what rate/under what exact conditions `ssd::perform` fails, since inspection of `src/ssd.rs` was not completed before the tool budget ran out; this should be verified in a follow-up before treating this as a high-confidence, high-severity finding.

### Citations

**File:** src/agents/image_notary.rs (L323-325)
```rust
                    Input::FinalizeSignup => {
                        self.finalize_signup()?;
                    }
```

**File:** src/agents/image_notary.rs (L341-352)
```rust
impl Agent {
    fn initialize_signup(&mut self) {
        self.save_dir = Path::new(DATA_ACQUISITION_BASE_DIR).join(self.signup_id.to_string());
        #[cfg(feature = "internal-data-acquisition")]
        ssd::perform(|| std::fs::create_dir_all(&self.save_dir));
        self.last_ir_save_time = Duration::ZERO;
        self.last_ir_face_save_time = Duration::ZERO;
        self.last_rgb_save_time = Duration::ZERO;
        self.last_thermal_save_time = Duration::ZERO;
        self.log = Log::default();
        self.sharpest_frames = SharpnessHeaps::default();
    }
```

**File:** src/agents/image_notary.rs (L354-362)
```rust
    #[cfg(not(feature = "internal-data-acquisition"))]
    #[allow(clippy::unnecessary_wraps)]
    fn finalize_signup(&mut self) -> Result<()> {
        // In theory this is not needed. Just an extra defensive measure.
        ssd::perform(|| {
            self.save_dir.exists().then(|| remove_dir_all(&self.save_dir)).unwrap_or(Ok(()))
        });
        Ok(())
    }
```
