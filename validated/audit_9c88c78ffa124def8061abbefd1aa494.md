### Title
`FinalizeSignup` skipped on error paths in `biometric_capture`, leaving `image_notary` agent enabled with stale signup state - ([File: src/plans/mod.rs])

### Finding Description
`Orb::start_image_notary` enables the `image_notary` agent and sends `InitializeSignup { signup_id }` [1](#0-0) . The only place the paired teardown happens is `Orb::stop_image_notary`, which sends `FinalizeSignup` and then calls `disable_image_notary` [2](#0-1) .

In `MasterPlan::biometric_capture`, the capture is produced by one of several extension plans or the basic plan, all invoked with the `?` operator: `plan.run(orb).await?` and the extension variants such as `biometric_capture::focus_sweep::Plan::from(plan).run(orb).await?` [3](#0-2) . `orb.stop_image_notary().await?` is only reached afterward, at line 1263 [4](#0-3) . Any `Err` returned by the capture plan's `run` therefore causes `biometric_capture` to return early via `?`, bypassing `stop_image_notary` entirely — `FinalizeSignup` is never sent and `disable_image_notary` (the broker-level cleanup) is never invoked from this function. There is no RAII guard (e.g. a `Drop` impl or `scopeguard`) tying `start_image_notary` to a guaranteed `stop_image_notary`/`FinalizeSignup`, so the pairing is enforced only by manual code sequencing, which is broken by any early `?`-propagated error between the two calls.

If a higher-level caller (e.g. `MasterPlan::run`) subsequently force-disables the agent without sending `FinalizeSignup`, the `image_notary` agent's internal task can be left in a state associated with the previous `signup_id` when the next signup's `InitializeSignup` is dispatched, since disabling only removes the broker's reference/handle and does not by itself guarantee the agent's internal per-signup state (e.g. `signup_id`, `sharpest_frames`) was reset via the normal `FinalizeSignup` protocol message.

### Impact Explanation
This is a cross-signup state-bleed / signup-state wedge: internal image-notary bookkeeping tied to one signup (`signup_id`, buffered sharpest frames) is not cleanly finalized before the next signup begins, violating the session-isolation invariant. Depending on how the agent's message-handling loop reacts to an out-of-order `InitializeSignup` while already mid-signup, this could manifest as an agent crash/`bail!` (denial of service against subsequent legitimate signups) or, in the worst case, incorrect association of frames/state across two different users' signups.

### Likelihood Explanation
Trigger requires only that the capture plan (`biometric_capture::Plan::run` or one of its extension wrappers) return an `Err` after `start_image_notary` succeeded — e.g. a capture-plan internal error, hardware/agent fault, or any other propagated failure during the capture loop, all of which occur on a normal, unprivileged signup attempt (no operator access needed). Because the fix-up/teardown pairing is manual rather than RAII-guarded, every one of the multiple call sites (`biometric_capture::Plan`, `focus_sweep`, `mirror_sweep`, `multi_wavelength`, `overcapture`) is equally exposed, making the gap easy to hit repeatedly.

### Recommendation
Guard `stop_image_notary`/`FinalizeSignup` with an RAII/defer pattern (e.g., a guard struct whose `Drop` sends `FinalizeSignup` and disables the agent, or wrap the fallible region in a helper that always finalizes regardless of `Ok`/`Err`) so that any early return between `start_image_notary` and `stop_image_notary` still finalizes/resets the `image_notary` agent's per-signup state before the broker allows a new `InitializeSignup` to be sent.

### Proof of Concept
Integration test plan:
1. Instrument/stub the capture plan (e.g. `biometric_capture::Plan::run`) to return `Err` deterministically after `start_image_notary` has been called (simulate a hardware/agent failure mid-capture).
2. Call `MasterPlan::biometric_capture` and assert that `Orb::stop_image_notary` (and thus `FinalizeSignup`) was never invoked, while `image_notary` remains in an "enabled" state or is torn down only via the higher-level disable path.
3. Immediately start a second signup (`start_image_notary` with a new `signup_id`), and assert on the `image_notary` agent's log/state that it either panics/`bail!`s, or incorrectly still references the previous `signup_id`/buffered frames instead of a clean reset — demonstrating the invariant "full state reset before next user" is violated.

Note: full confirmation of the exact downstream behavior (whether `MasterPlan::run`'s error-path cleanup at mod.rs around line 373 calls `disable_image_notary` directly, and the precise `image_notary` agent reaction to an out-of-order `InitializeSignup`) could not be completed within the available tool budget; this should be verified directly against `src/agents/image_notary.rs`'s message loop and `MasterPlan::run` before treating severity as final.

### Citations

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

**File:** src/brokers/orb.rs (L868-879)
```rust
    /// Stops the image notary agent.
    ///
    /// # Panics
    ///
    /// If the agent is not enabled.
    pub async fn stop_image_notary(&mut self) -> Result<image_notary::Log> {
        let image_notary = self.image_notary.enabled().expect("image_notary is not enabled");
        image_notary.send(port::Input::new(image_notary::Input::FinalizeSignup)).await?;
        let image_notary_log = image_notary::take_log(image_notary).await?;
        self.disable_image_notary();
        Ok(image_notary_log)
    }
```

**File:** src/plans/mod.rs (L1188-1211)
```rust
                qr_scan::user::SignupMode::PupilContractionExtension => {
                    tracing::info!("Pupil Contraction extension: activated");
                    biometric_capture::pupil_contraction::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::FocusSweepExtension => {
                    tracing::info!("Focus Sweep extension: activated");
                    biometric_capture::focus_sweep::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::MirrorSweepExtension => {
                    tracing::info!("Mirror Sweep extension: activated");
                    biometric_capture::mirror_sweep::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::MultiWavelength => {
                    tracing::info!("Multi-wavelength extension: activated");
                    biometric_capture::multi_wavelength::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::Overcapture => {
                    tracing::info!("Overcapture extension: activated");
                    biometric_capture::overcapture::Plan::from(plan).run(orb).await?
                }
                qr_scan::user::SignupMode::Basic => plan.run(orb).await?,
            }
        } else {
            plan.run(orb).await?
```

**File:** src/plans/mod.rs (L1263-1263)
```rust
        let image_notary_log = orb.stop_image_notary().await?;
```
