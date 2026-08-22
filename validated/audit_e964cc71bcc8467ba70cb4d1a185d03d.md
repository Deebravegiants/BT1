This is a genuine architectural match to the reported bug class. The orb's backend-controlled `Config` (analogous to zAuction's privileged admin) can flip signup-authorization-critical flags — most notably `ignore_user_centric_signups` — at any time with no time lock, no advance notice, and no validation beyond a bounds check on `sound_volume`. Because this flag is read live, deep inside an in-progress signup rather than snapshotted at signup start, a backend-pushed config change landing mid-signup changes whether local biometric enrollment/fraud detection is even executed for that specific signup.

### Title
Unvalidated, non-timelocked live config toggling of `ignore_user_centric_signups` allows mid-signup bypass of local enrollment/fraud pipeline - (File: src/plans/mod.rs)

### Summary
The Orb periodically downloads a `Config` object from the backend and atomically swaps it into a shared `Arc<Mutex<Config>>` with no time lock, no staged rollout, and no validation of security-relevant fields [1](#0-0) . One of these fields, `ignore_user_centric_signups`, is read live — not snapshotted — at the exact moment the master signup plan decides whether to trust a client-reported "user-centric" signup as already-verified or to run the full local enrollment/fraud-detection pipeline [2](#0-1) . Because the flag is fetched fresh from the mutex at that specific point rather than being fixed for the duration of a signup, a backend-side config update landing in the small window between the start of a signup and this check can flip the outcome for an in-flight signup, exactly mirroring the "admin changes take effect immediately, unpredictably, mid-transaction" issue in the reported zAuction finding.

### Finding Description
`Config::download` fetches the latest configuration from `backend::config::request()` and constructs a new `Config` via `Config::from_backend`, whose only validation gate is `Config::validate`, which checks nothing but `sound_volume <= MAX_SOUND_VOLUME` [3](#0-2) . This new config completely replaces the old one: `Config::download_and_store` does `*config.lock().await = Self::download().await?...` [4](#0-3) , and the periodic background task in `Observer::config_update` performs the same unconditional swap every `CONFIG_UPDATE_INTERVAL` [1](#0-0) .

Inside `MasterPlan::do_signup`, the flag `ignore_user_centric_signups` is read directly from the shared mutex at the moment the enrollment decision is made:
```
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups {
    // trust the app-reported user_centric_signup flag, treat as enrollment success
} else {
    // run enroll_user::Plan -> the actual local biometric enrollment / server verification
};
``` [2](#0-1) 

Other config values consumed earlier in the same signup (`self_serve`, `operator_qr_expiration_time`, etc.) are read once at the top of `MasterPlan::run` for that loop iteration [5](#0-4) , but `ignore_user_centric_signups` is not part of that snapshot — it is re-fetched live later in the same signup's execution. There is no time lock, no staged/2-step config commit, and no requirement that a config value be stable for the duration of an in-progress signup — the exact class of problem described in the report ("updating ... takes effect immediately," "purely accidental negative effects... due to unfortunate timing of changes").

### Impact Explanation
If the backend toggles `ignore_user_centric_signups` from `false` to `true` while a signup is in flight and `user_centric_signup` is `true` for that session, the branch at `src/plans/mod.rs:639` skips `enroll_user` entirely and marks the signup's enrollment status based solely on `signup_reason == SignupReason::Normal` [6](#0-5)  — i.e., the app/client-asserted "already verified" signup is accepted without the Orb re-running its own local enrollment/verification request for that specific signup. Conversely, flipping it the other way mid-flight forces re-enrollment for a signup that had already begun under different assumptions, producing state inconsistent with what was reported to the user or app. Either direction produces the same unpredictability the report flags: users (or the signup pipeline itself) cannot be sure which enrollment/verification path a given signup will take, because the answer can change during the signup's own execution window, potentially leading to misattributed signup completion status.

### Likelihood Explanation
The config endpoint is polled unconditionally on a fixed interval by `Observer::config_update` for the whole lifetime of the process, independent of whether a signup is currently in progress [1](#0-0) , and the resulting `Config` is applied immediately with no coordination with in-flight signups. Any signup whose duration straddles a config refresh interval is exposed; no attacker interaction beyond controlling/observing the backend-served config is required, and no additional validation exists to prevent this field from being toggled in either direction at any time.

### Recommendation
Snapshot all signup-behavior-relevant config values (in particular `ignore_user_centric_signups`, along with `self_serve*`, `pcp_v3`, `user_qr_validation_*`) once at the start of a signup and use that fixed snapshot for the entire signup's lifetime, rather than re-reading the shared, live-mutable `Config` at each decision point. Additionally, apply backend-pushed config changes only between signups (e.g., gate `config_update` while `signup_flag` is set, similar to how `network_unblocked` already gates it) and consider validating/rate-limiting changes to security-relevant boolean flags, consistent with the report's broader recommendation of advance notice/timelocking for behavior-altering privileged updates.

### Proof of Concept
1. Start a signup where the mobile app reports `user_centric_signup = true` (`qr_codes.user_data.user_centric_signup`).
2. While the signup is between `start_signup` and the check at `src/plans/mod.rs:639` (a window that includes biometric capture, pipeline processing, and PCP building), have the backend serve an updated `/api/v1/orbs/{id}` config response with `IgnoreUserCentricSignups: false` (or toggle it away from a previously-effective `true`).
3. `Observer::config_update`'s background task (running on `CONFIG_UPDATE_INTERVAL`) downloads and swaps in the new config via `*config.lock().await = new_config` before the signup reaches line 639.
4. When execution reaches `orb.config.lock().await.ignore_user_centric_signups`, it observes the newly-swapped value rather than whatever was in effect when the signup began, causing the enrollment path taken (`enroll_user` local pipeline vs. trusting `user_centric_signup`) to diverge from what any party observing the start of the signup would have expected.

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

**File:** src/plans/mod.rs (L328-336)
```rust
    pub async fn run(&mut self, orb: &mut Orb) -> Result<()> {
        let Config {
            self_serve,
            self_serve_button,
            orb_relay_shutdown_wait_for_pending_messages,
            orb_relay_shutdown_wait_for_shutdown,
            operator_qr_expiration_time,
            ..
        } = *orb.config.lock().await;
```

**File:** src/plans/mod.rs (L639-656)
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
```

**File:** src/config.rs (L322-352)
```rust
    /// Validates the configuration.
    #[must_use]
    pub fn validate(&self) -> bool {
        self.basic_config.sound_volume <= MAX_SOUND_VOLUME
    }

    async fn load() -> Result<Self> {
        let path = config_file_path();
        tracing::info!("Loading config from {}", path.display());
        let contents = fs::read_to_string(path).await?;
        tracing::debug!("Config file contents: {contents:#?}");
        Ok(Self { basic_config: serde_json::from_str(&contents)?, ..Self::default() })
    }

    /// Downloads the latest configuration from the backend and updates the
    /// shared configuration object.
    pub async fn download() -> Result<Config> {
        let res = backend::config::request().await.map_err(|e| {
            tracing::error!("Config request failed: {:?}", e);
            dd_incr!("main.count.http.config_update.error");
            e
        })?;

        if let Some(config) = Config::from_backend(res) {
            dd_incr!("main.count.http.config_update.success");
            Ok(config)
        } else {
            dd_incr!("main.count.http.config_parse.error");
            Err(eyre!("invalid config"))
        }
    }
```

**File:** src/config.rs (L357-368)
```rust
    pub async fn download_and_store(config: Arc<Mutex<Config>>) -> Result<()> {
        *config.lock().await = Self::download().await.map_err(|e| {
            tracing::error!("Failed to download config: {:?}", e);
            e
        })?;
        let config_to_store = config.lock().await;
        tracing::info!("Downloaded latest config: {:?}", config_to_store);
        config_to_store.store().await.map_err(|e| {
            tracing::error!("Config downloaded but failed to be stored: {:?}", e);
            e
        })
    }
```
