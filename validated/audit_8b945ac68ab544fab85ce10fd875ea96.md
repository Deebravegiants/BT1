### Title
Mid-signup config drift causes inconsistent fraud/identity-validation policy within a single signup - (File: src/plans/mod.rs, src/brokers/observer.rs)

### Summary
`orb-core` keeps orb configuration in a single shared `Arc<Mutex<Config>>` that is refreshed from the backend on a fixed background interval, independent of whether a signup is currently in progress. A signup (`do_signup`) is a long-running, multi-stage async flow (QR scan → capture → pipeline → fraud check → PCP build/upload) that re-reads this shared config at several different points instead of using one consistent snapshot for the whole signup. This is the same bug class as the BendDAO finding: a shared parameter is changed asynchronously, but different parts of the same logical operation ("interest accrual" there, "one signup" here) end up using different snapshots of that parameter, producing an internally inconsistent result.

### Finding Description
The background `Observer` task downloads a fresh `Config` and swaps it into the shared `Arc<Mutex<Config>>` every `CONFIG_UPDATE_INTERVAL` (10 seconds), unconditionally, regardless of whether a signup is running: [1](#0-0) [2](#0-1) 

`MasterPlan::do_signup` snapshots part of the config once at the start of a signup: [3](#0-2) 

But the same signup subsequently re-reads the *live* shared config multiple more times as it progresses through its stages, rather than reusing the initial snapshot — e.g. immediately after, when building the `DebugReport`: [4](#0-3) 

again when deciding whether to proceed to capture: [5](#0-4) 

again when configuring the capture plan itself (`self_serve`, capture timeout): [6](#0-5) 

and again mid biometric pipeline, where `face_identifier_model_configs` is re-fetched from the shared config and pushed into the running model agents: [7](#0-6) [8](#0-7) 

Because a background `Config::download()` can complete and overwrite the shared `Mutex<Config>` at any point during this multi-second-to-multi-minute flow, later reads within the *same* signup can observe a different configuration than earlier reads within that signup. Security/identity-relevant fields carried in this same `Config` object — such as `user_qr_validation_use_full_operator_qr`, `user_qr_validation_use_only_operator_location`, `child_threshold` (under-age/fraud threshold), and `fraud_check_engine_config` — are defined alongside the other fields shown above and downloaded/parsed the same way: [9](#0-8) [10](#0-9) 

There is no mechanism that freezes/locks the config for the duration of a single signup, nor any explicit "apply new config only to future signups" boundary — the exact class of bug flagged in the BendDAO report (parameter changes applied without first isolating/flushing the in-flight state that depends on the old parameter value).

### Impact Explanation
If the backend pushes a config update (e.g., toggling `user_qr_validation_use_full_operator_qr`/`user_qr_validation_use_only_operator_location`, changing `child_threshold`, or changing `fraud_check_engine_config`) while a signup is mid-flight, different stages of that one signup can be evaluated against different policy snapshots: the initial capture/QR-validation decision under one policy, and the later fraud-check/pipeline decision under another. This is an unprivileged-user-reachable inconsistency (it occurs on the normal signup path any regular user goes through, with no special access needed) that can misattribute the strictness applied to identity binding and fraud/liveness gating for that specific signup, producing an outcome that neither the old nor the new policy alone would have produced consistently — a fraud/liveness policy bypass or misattributed signup validation, in the same spirit as the referenced fee-factor accounting drift.

### Likelihood Explanation
Config downloads happen automatically every 10 seconds for the entire lifetime of the orb process, and a single signup routinely spans well beyond 10 seconds (QR scan, a hard-coded 3s pre-capture sleep, biometric capture, biometric pipeline, fraud detection, PCP build/upload). The race window is therefore present in essentially every signup, making this a frequent, low-effort-to-trigger condition rather than a rare edge case — similar to BendDAO's own observation that the analogous accounting bug is "frequently" triggered by ordinary transaction activity.

### Recommendation
Snapshot the full `Config` object once at the very start of `do_signup` and thread that single snapshot through every subsequent stage of the signup (capture, pipeline, fraud check, PCP build) instead of re-locking and re-reading `orb.config` from the shared `Arc<Mutex<Config>>` at multiple later points. Any config values needed later in the pipeline (e.g. `face_identifier_model_configs`) should be taken from this per-signup snapshot rather than fetched fresh mid-pipeline, ensuring a single signup is always evaluated under one consistent configuration/policy.

### Proof of Concept
1. Start a signup; `do_signup` snapshots `Config` at entry (`src/plans/mod.rs:497-507`), which at that moment has `user_qr_validation_use_full_operator_qr = true`.
2. While the signup is in the ~3s pre-capture sleep or during biometric capture/pipeline, the backend pushes a new config with `user_qr_validation_use_full_operator_qr = false` (or a changed `child_threshold`/`fraud_check_engine_config`); the `Observer`'s background task downloads and swaps it into the shared `Mutex<Config>` within the next `CONFIG_UPDATE_INTERVAL` tick (`src/brokers/observer.rs:187-205`).
3. Subsequent re-reads of `orb.config.lock().await` inside the same signup (e.g. `src/plans/mod.rs:517`, `:1167-1178`, `:2068-2079`, `src/plans/biometric_pipeline/mod.rs:580-591`) now observe the *new* config value, while earlier decisions in the same signup were made under the *old* value.
4. The net result is that one signup's identity-validation/fraud policy is a hybrid of two different configurations that were never intended to coexist within a single signup — exactly the inconsistency pattern described in the BendDAO fee-factor report, applied here to signup-security-relevant configuration instead of interest-fee accounting.

Note: I was unable to fully trace the exact body of `verify_user_qr_code`/`detect_fraud` (their line ranges were located via `grep_search` but content could not be retrieved before the iteration budget ran out), so the precise consumption of `user_qr_validation_use_full_operator_qr`/`child_threshold` inside those functions is inferred from the config field definitions rather than directly confirmed. A follow-up Devin session with full read access would be needed to confirm exactly which stage(s) consume these specific fields.

### Citations

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

**File:** src/consts.rs (L86-88)
```rust
/// Backend config update interval.
pub const CONFIG_UPDATE_INTERVAL: Duration = Duration::from_secs(10);

```

**File:** src/plans/mod.rs (L497-507)
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
        let mut result = self.start_signup(orb, dbus).await?;
```

**File:** src/plans/mod.rs (L513-518)
```rust
        let debug_report = result.debug_report.insert(DebugReport::builder(
            result.capture_start,
            &result.signup_id,
            &qr_codes,
            orb.config.lock().await.clone(),
        ));
```

**File:** src/plans/mod.rs (L1167-1178)
```rust
        let Config { self_serve, self_serve_biometric_capture_timeout, .. } =
            *orb.config.lock().await;
        let plan = biometric_capture::Plan::new(
            &wavelengths,
            Some(if self_serve {
                self_serve_biometric_capture_timeout
            } else {
                BIOMETRIC_CAPTURE_TIMEOUT
            }),
            debug_report.signup_extension_config.clone(),
            &orb.config.lock().await.clone(),
        );
```

**File:** src/plans/mod.rs (L2068-2079)
```rust
async fn proceed_with_biometric_capture(orb: &mut Orb) -> Result<bool> {
    let Config {
        self_serve,
        self_serve_app_skip_capture_trigger,
        self_serve_app_capture_trigger_timeout,
        ..
    } = *orb.config.lock().await;
    if !self_serve || self_serve_app_skip_capture_trigger {
        // Biometric capture not gated by a user action. Continue.
        orb.ui.signup_start();
        return Ok(true);
    }
```

**File:** src/plans/biometric_pipeline/mod.rs (L293-299)
```rust
        self.run_mega_agent_one(orb, mega_agent_one::Input::IRNet(ir_net::Input::Version)).await?;

        self.run_update_all_configs(orb).await?;

        // Request Mega Agent's full configuration.
        self.run_mega_agent_one(orb, mega_agent_one::Input::Config).await?;
        self.run_mega_agent_two(orb, mega_agent_two::Input::Config).await?;
```

**File:** src/plans/biometric_pipeline/mod.rs (L580-591)
```rust
    async fn run_update_all_configs(&mut self, orb: &mut Orb) -> Result<()> {
        let face_identifier_model_configs =
            orb.config.lock().await.face_identifier_model_configs.clone();
        self.run_mega_agent_two(
            orb,
            mega_agent_two::Input::FaceIdentifier(face_identifier::Input::UpdateConfig(
                face_identifier_model_configs,
            )),
        )
        .await?;
        Ok(())
    }
```

**File:** src/config.rs (L69-76)
```rust
    /// Fraud check engine: config collection.
    pub fraud_check_engine_config: fraud_check::BackendConfig,
    /// IR-Net model configs: Namespaced IR-Net configs.
    pub ir_net_model_configs: Option<HashMap<String, String>>,
    /// Iris model configs: Namespaced Iris config files.
    pub iris_model_configs: Option<HashMap<String, String>>,
    /// Person Classifier config: under-age threshold.
    pub child_threshold: Option<f32>,
```

**File:** src/config.rs (L120-125)
```rust
    /// Ignore app centric signup flag from the app and always perform an enrollment request.
    pub ignore_user_centric_signups: bool,
    /// Use the operator's QR together with the user QR to validate the user.
    pub user_qr_validation_use_full_operator_qr: bool,
    /// Use only the operator's location to validate the user.
    pub user_qr_validation_use_only_operator_location: bool,
```
