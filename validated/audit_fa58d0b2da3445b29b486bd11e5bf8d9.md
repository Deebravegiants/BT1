### Title
Signup enrollment path (`ignore_user_centric_signups`) can flip mid-signup due to background config updates racing with in-progress verification decisions - (File: src/plans/mod.rs)

### Summary
This is an analog of the Llama "opcode determined after approval" bug class. In `LlamaCore`, an action's approved intent (call vs. delegatecall) is not fixed at approval time — it is re-evaluated later against `authorizedScripts`, a mapping that unrelated actions can mutate. In orb-core, the decision of *whether a signup will undergo backend-side identity verification at all* is similarly not fixed at the start of the signup: it is re-evaluated later in `do_signup` against a shared, globally mutable `Config.ignore_user_centric_signups` flag that a background task can flip at any time, independent of and uncorrelated with the specific signup in progress.

### Finding Description
`MasterPlan::do_signup` takes an initial snapshot of the shared `Arc<Mutex<Config>>` at the top of the function: [1](#0-0) 

Note that `ignore_user_centric_signups` is **not** part of that snapshot. Later in the same function, after biometric capture, fraud detection, and PCP-building have already run and a `signup_reason` has already been computed, the code re-locks the config a second, independent time to decide the enrollment path: [2](#0-1) 

If `user_centric_signup && !ignore_user_centric_signups` is true, the code takes the "trust the app" branch: it marks the signup successful purely based on `signup_reason == SignupReason::Normal`, without ever calling backend verification (`enroll_user`, which posts to `signup_post`/`signup_poll` and lets the backend confirm/reject duplicates, fraud, or invalid signatures). Otherwise, it calls `Box::pin(self.enroll_user(...))`, which performs full backend-verified enrollment: [3](#0-2) 

The value of `ignore_user_centric_signups` is not tied to the specific signup at all — it comes from the shared `Config` object, which is independently and asynchronously overwritten by a background task that periodically re-downloads config from the backend on a fixed interval, completely decoupled from any particular signup's lifecycle: [4](#0-3) [5](#0-4) 

This background update runs continuously as long as the network is unblocked, with no gating on whether a signup is currently in progress (`signup_flag` is not consulted in `poll_extra`/`config_update`): [6](#0-5) 

Just like the Llama action whose approved semantics (call vs. delegatecall) could be silently altered by an unrelated action changing `authorizedScripts` after approval, here the semantics of "will this signup be cryptographically/backend verified" is decided by re-reading a value that an entirely unrelated process (a scheduled config refresh, driven by the backend/ops, not by anything about this user or this signup) can change at any point during the multi-second signup flow (capture, fraud detection, PCP build all happen between the two config reads).

### Impact Explanation
If `ignore_user_centric_signups` is `false` at the start of a signup (so the operator/system expects backend verification to run) but flips to `true` due to a background config refresh landing between the initial config snapshot and the check at line 639, an app-centric ("user_centric") signup that was supposed to be verified against the backend (catching duplicate signups, fraud flags, or invalid signatures) instead gets silently accepted as successful solely based on the local `signup_reason` computed from the local fraud pipeline, bypassing the backend's authoritative verification step. This is a concrete verification/fraud-bypass and potential misattributed-signup impact: a signup can be marked `Success` and its PCP/tier data uploaded and attributed to a user identity without ever confirming with the backend that the signup should be accepted (e.g., not a duplicate, not previously flagged, signature not required to be recomputed via `enroll_user`'s `signup_post`).

### Likelihood Explanation
The config-refresh interval (`CONFIG_UPDATE_INTERVAL`) runs continuously in the background regardless of whether a signup is active, and a full signup flow (QR scan, biometric capture, pipeline, fraud checks, PCP build) spans multiple seconds — a large enough window for at least one config refresh to land in between the two independent reads of the config mutex. No additional attacker action is required beyond normal operational config pushes changing this flag (e.g., during a rollout/rollback of the user-centric-signup feature), which is a realistic operational scenario rather than a contrived one.

### Recommendation
Take a single, consistent snapshot of all config values relevant to a signup's enrollment-path decision (including `ignore_user_centric_signups`) once at the start of `do_signup`, and use that same snapshot for every branch decision made throughout the signup, rather than re-locking and re-reading `orb.config` at a later point in the same signup. This ensures the enrollment/verification semantics decided for a signup cannot be altered mid-flight by an unrelated background config update.

### Proof of Concept
1. Start a signup as an app-centric ("user_centric") user with `ignore_user_centric_signups = false` in the currently-loaded `Config` — `do_signup` begins, taking its initial config snapshot at src/plans/mod.rs:497-506 (which does not include `ignore_user_centric_signups`).
2. While biometric capture, the biometric pipeline, and fraud detection run (multi-second window), the background `Observer::config_update` task (src/brokers/observer.rs:187-205, triggered every `CONFIG_UPDATE_INTERVAL` per src/brokers/observer.rs:475-480) fires and downloads a new backend config that now has `ignore_user_centric_signups = true` (e.g., due to an unrelated ops rollout), overwriting `*config.lock().await` in place.
3. `do_signup` reaches the enrollment-path decision at src/plans/mod.rs:639 and re-locks the config, now observing `ignore_user_centric_signups = true`.
4. The signup takes the "trust user_centric_signup" branch and is marked `Success`/`Status::Success` purely from the local `signup_reason`, without ever invoking `enroll_user`/`signup_post`/`signup_poll` backend verification (src/plans/enroll_user.rs:90-103), even though the operational expectation at signup-start time was that backend verification would occur.

### Citations

**File:** src/plans/mod.rs (L497-506)
```rust
        let Config {
            self_serve,
            pcp_v3,
            orb_relay_announce_orb_id_retries,
            orb_relay_announce_orb_id_timeout,
            orb_relay_shutdown_wait_for_pending_messages,
            orb_relay_shutdown_wait_for_shutdown,
            operator_qr_expiration_time,
            ..
        } = *orb.config.lock().await;
```

**File:** src/plans/mod.rs (L639-663)
```rust
        let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
        {
            debug_report.enrollment_status(match signup_reason {
                SignupReason::Normal => enroll_user::Status::Success,
                _ => enroll_user::Status::Error,
            });
            signup_reason == SignupReason::Normal
        } else {
            Box::pin(self.enroll_user(
                orb,
                debug_report,
                &capture,
                pipeline.as_ref(),
                signup_reason,
            ))
            .await
            .is_success()
        };

        Self::report_signup_reason(success, signup_reason, debug_report);

        result.success =
            debug_report.enrollment_status.as_ref().map_or(false, enroll_user::Status::is_success);
        Ok(result)
    }
```

**File:** src/plans/enroll_user.rs (L90-103)
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
            match response {
```

**File:** src/brokers/observer.rs (L187-205)
```rust
    fn config_update(&mut self, observer: &mut Observer) -> Result<()> {
        if self.before_config_update()? {
            match observer.config_update.as_mut().map(future::FutureExt::now_or_never) {
                Some(None) => return Ok(()),
                Some(Some(result)) => result??,
                None => {}
            }
            let config = Arc::clone(&observer.config);
            let ui = observer.ui.clone();
            observer.config_update = Some(tokio::spawn(async move {
                if let Ok(new_config) = Config::download().await {
                    *config.lock().await = new_config;
                    config.lock().await.propagate_to_ui(ui.as_ref());
                }
                Ok(())
            }));
        }
        Ok(())
    }
```

**File:** src/brokers/observer.rs (L442-480)
```rust
    fn poll_extra(
        &mut self,
        plan: &mut dyn Plan,
        cx: &mut Context<'_>,
        _fence: Instant,
    ) -> Result<Option<Poll<()>>> {
        while let Poll::Ready(report) = self.net_monitor.poll_next_unpin(cx) {
            self.network_unblocked = true;
            self.handle_net_monitor(report.ok_or_else(|| eyre!("network monitor exited"))?);
        }
        while let Poll::Ready(output) = self.main_mcu.rx_mut().next_broadcast().poll_unpin(cx) {
            if matches!(self.handle_mcu(plan, output?)?, BrokerFlow::Break) {
                return Ok(Some(Poll::Ready(())));
            }
        }
        if let Poll::Ready(()) = self.button_long_press_timer.poll_unpin(cx) {
            tracing::debug!("Button long press");
            tracing::info!("Shutdown requested by the user");
            self.ui.shutdown(true);
            return Ok(Some(Poll::Ready(())));
        }
        if let Poll::Ready(()) = self.button_double_press_timer.poll_unpin(cx) {
            tracing::debug!("Button double press");
            self.button_press_sequence.clear();
            handle_double_press(self);
        }
        while let Poll::Ready(report) = self.ssd_rx.poll_recv(cx) {
            if let Some(report) = report {
                self.handle_ssd_health_check(&report);
            } else {
                bail!("SSD health check failed");
            }
        }
        if self.network_unblocked {
            while self.config_update_interval.next().poll_unpin(cx).is_ready() {
                plan.config_update(self)?;
            }
            plan.poll_status_update(self, cx)?;
        }
```
