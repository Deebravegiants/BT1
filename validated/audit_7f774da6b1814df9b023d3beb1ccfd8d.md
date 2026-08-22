### Title
Late biometric-frame messages processed after `FinalizeSignup` are mislabeled into the next signup's directory in `image_notary::Agent` - (File: `src/agents/image_notary.rs`)

### Summary
The Crowdsale bug allowed `_addCommitment()` to keep mutating shared state (`commitments[]`) after `finalize()` had already computed and locked in the final distribution, because `_addCommitment()` never checked `status.finalized`/`auctionEnded()`. The analogous pattern exists in `orb-core`'s `image_notary::Agent::run`: `Input::FinalizeSignup` is handled but does not exit the inner message loop, and the shared mutable fields `self.signup_id` / `self.save_dir` / `self.log` / `self.sharpest_frames` are only reset when the *next* `Input::InitializeSignup` arrives, with no versioning/guard tying in-flight `Save*` messages to the signup they were produced for.

### Finding Description
`Agent::run` in `src/agents/image_notary.rs` implements a single mutable-state machine keyed on `self.signup_id`/`self.save_dir`: [1](#0-0) 

- `Input::FinalizeSignup` calls `finalize_signup()` (which either deletes `save_dir` or persists `sharpest_frames`) but **does not break/continue the inner loop**, so the agent keeps accepting `Save*` messages for the same iteration.
- `Input::TakeLog` is the only variant that does `continue 'signup`, returning control to the outer loop where the *next* `InitializeSignup` will overwrite `self.signup_id`, `self.save_dir`, `self.log`, and `self.sharpest_frames` via `initialize_signup()`. [2](#0-1) 

The orchestration in the broker calls `FinalizeSignup` then `TakeLog` then disables the agent: [3](#0-2) 

and a fresh signup re-initializes the same agent instance via `start_image_notary`: [4](#0-3) 

Crucially, `Save*` inputs (`SaveIrNetEstimate`, `SaveIrFaceData`, `SaveRgbNetEstimate`, `SaveThermalData`, `SaveIdentificationImages`) are **not sent exclusively by the sequential `MasterPlan` flow that calls `stop_image_notary`**; they originate from the independent, concurrently-running AI pipeline agents (`mega_agent_one`/`mega_agent_two`) that stream frame estimates back to the broker as they complete inference, and those handlers tag saved data using `self.signup_id`/`self.save_dir` read at *processing* time, not at message-creation time: [5](#0-4) 

Because the agent's identity fields are ordinary `&mut self` fields with no per-message "which signup do I belong to" tag or generation counter, any `Save*` message that was queued for signup A but is processed by the agent's single inner loop *after* `TakeLog`/`FinalizeSignup` has advanced to `initialize_signup()` for signup B will be written into signup B's directory and appended to signup B's `Log`, using B's `signup_id` for the `image_id`. This mirrors the Crowdsale root cause exactly: a state-mutating operation (`_addCommitment` / `Save*`) is not gated on the finalize/auctionEnded checkpoint (`status.finalized` / signup-boundary), so an "extra" side-effect that was legitimately in flight for the old context is silently applied to the new context instead of being rejected or quarantined.

### Impact Explanation
If a late frame estimate/image belonging to User A's capture is processed by `image_notary` after finalization and after User B's `InitializeSignup` has already reset the shared fields, User A's biometric artifact (IR-Net estimate, RGB-Net estimate, thermal frame, or identification image) gets written to disk and logged under User B's `signup_id`. This is a concrete cross-signup state bleed: biometric capture data collected for one user can be misattributed to, and bundled/uploaded as part of, a different user's debug report / identification-image bundle (`upload_debug_report`, `save_identification_images`), which is a biometric-data-disclosure/misattribution concern rather than a purely internal bookkeeping error.

### Likelihood Explanation
The race requires that a `Save*` message produced by the AI pipeline for the just-finished signup is still queued/in-flight when the plan calls `stop_image_notary()` and a subsequent signup starts quickly (e.g., in loop-mode operation with rapid successive signups, or when the pipeline lags behind due to GPU/model latency). Because there is no explicit drain/flush barrier or per-message signup tag enforced on the `image_notary` port beyond ordering, and the agent processes `FinalizeSignup` without terminating the accepting loop, this is plausible under normal pipeline back-pressure rather than requiring privileged access — it is a timing/ordering issue reachable purely through normal, repeated unprivileged signup flows.

### Recommendation
Tag every `Save*`/`FinalizeSignup` message with the `SignupId` it was generated for (already available on most `Save*Input` structs' originating frames), and have the handlers reject/drop messages whose `signup_id` does not match `self.signup_id` at processing time — analogous to adding the `auctionEnded()`/`status.finalized` guard inside `_addCommitment()`. Additionally, make `FinalizeSignup` transition the agent into a "finalized" state that refuses further `Save*` inputs until the next `InitializeSignup`, and ensure `stop_image_notary`/`start_image_notary` cannot race (e.g. by draining/flushing all pending pipeline messages before issuing `InitializeSignup` for the next signup).

### Proof of Concept
1. Start signup A; `mega_agent_two` begins producing `SaveRgbNetEstimate` messages for A's frames via the broker.
2. Biometric capture for A completes; `MasterPlan` calls `orb.stop_image_notary()`, which sends `FinalizeSignup` then `TakeLog` to the `image_notary` port — the agent `continue 'signup`s back to the outer loop awaiting a new `InitializeSignup`.
3. Due to pipeline latency, one more `SaveRgbNetEstimate` message for signup A (produced before finalize but delivered after `TakeLog` was processed) is still in the channel.
4. Signup B starts; `orb.start_image_notary(signup_id_B)` sends `InitializeSignup { signup_id: signup_id_B }`, which the agent processes, resetting `self.signup_id`/`self.save_dir` to B.
5. If A's delayed `SaveRgbNetEstimate` is delivered to the port after step 4 (channel ordering not guaranteed to reflect production time across independently-firing agents), `handle_save_rgb_net_estimate` writes/logs the data using `self.signup_id == signup_id_B`, embedding user A's frame/estimate into user B's signup artifacts.

### Citations

**File:** src/agents/image_notary.rs (L286-338)
```rust
    fn run(mut self, mut port: port::Inner<Self>) -> Result<(), Self::Error> {
        let rt = runtime::Builder::new_current_thread().enable_all().build()?;
        'signup: while let Some(input) = rt.block_on(port.next()) {
            self.signup_id = match input.value {
                Input::InitializeSignup { signup_id } => signup_id,
                input => bail!("Unexpected image_notary input: {input:?}"),
            };
            ensure_enough_space().wrap_err("auto deletion")?;
            tracing::debug!(
                "There is {} bytes available on the SSD before signup",
                ssd::available_space()
            );
            self.initialize_signup();
            while let Some(input) = rt.block_on(port.next()) {
                match input.value {
                    // These saved images are currently unused, but helpful for debugging
                    Input::SaveIdentificationImages(input) => {
                        self.handle_save_identification_images(*input)?;
                    }
                    Input::SaveIrNetEstimate(input) => {
                        self.handle_save_ir_net_estimate(input, &mut port)?;
                    }
                    Input::SaveIrFaceData(input) => {
                        self.handle_save_ir_face_data(input, &mut port)?;
                    }
                    Input::SaveRgbNetEstimate(input) => {
                        self.handle_save_rgb_net_estimate(input)?;
                    }
                    Input::SaveFusionRnFi(input) => {
                        self.handle_save_fusion_rn_fi(input)?;
                    }
                    Input::SaveThermalData(input) => {
                        self.handle_save_thermal_data(input, &mut port)?;
                    }
                    Input::GetSharpestFrame(input) => {
                        self.handle_get_sharpest_frame(input);
                    }
                    Input::FinalizeSignup => {
                        self.finalize_signup()?;
                    }
                    Input::TakeLog(log_tx) => {
                        let _ = log_tx.send(take(&mut self.log));
                        continue 'signup;
                    }
                    input @ Input::InitializeSignup { .. } => {
                        bail!("Unexpected image_notary input: {input:?}")
                    }
                }
            }
            break;
        }
        Ok(())
    }
```

**File:** src/agents/image_notary.rs (L341-362)
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

**File:** src/agents/image_notary.rs (L405-418)
```rust
    fn handle_save_ir_net_estimate(
        &mut self,
        input: SaveIrNetEstimateInput,
        port: &mut port::Inner<Self>,
    ) -> Result<()> {
        let SaveIrNetEstimateInput {
            estimate,
            frame,
            wavelength,
            target_left_eye,
            fps_override,
            log_metadata_always,
        } = input;
        let image_id = frame.image_id(&self.signup_id);
```

**File:** src/brokers/orb.rs (L777-786)
```rust
    /// Initializes the image_notary agent with the given `signup_id`.
    pub async fn start_image_notary(&mut self, signup_id: SignupId) -> Result<()> {
        self.enable_image_notary()?;
        self.image_notary
            .enabled()
            .unwrap()
            .send(port::Input::new(image_notary::Input::InitializeSignup { signup_id }))
            .await?;
        Ok(())
    }
```

**File:** src/brokers/orb.rs (L873-879)
```rust
    pub async fn stop_image_notary(&mut self) -> Result<image_notary::Log> {
        let image_notary = self.image_notary.enabled().expect("image_notary is not enabled");
        image_notary.send(port::Input::new(image_notary::Input::FinalizeSignup)).await?;
        let image_notary_log = image_notary::take_log(image_notary).await?;
        self.disable_image_notary();
        Ok(image_notary_log)
    }
```
