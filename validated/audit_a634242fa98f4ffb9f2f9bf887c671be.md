### Title
Inconsistent Backend Config Snapshot Across a Single Signup Enables Mismatched Fraud/Age-Verification Enforcement - (File: src/plans/mod.rs)

### Summary
`Config` is shared across the whole Orb process as `Arc<Mutex<Config>>` and can be refreshed at any time from the backend independently of an in-progress signup [1](#0-0) . Instead of being snapshotted once for the duration of a signup, `do_signup` and its sub-routines each independently re-lock and re-read `orb.config` at different points in time during the *same* signup, so a backend-triggered config change mid-signup can cause different phases of one signup to observe different values of the same logically-related settings. This is the same bug class as the reported `_originationFeeRate` issue: a caller-relevant parameter is captured/used at one point but a mutable, externally-updatable value is actually applied with whatever its value happens to be at a later point in the same transaction/session, producing unintended, inconsistent behavior.

### Finding Description
`do_signup` destructures several config fields once near the start of the signup: `self_serve`, `pcp_v3`, relay flags, and `operator_qr_expiration_time` [2](#0-1) . Later, other independent methods called within the very same signup re-acquire the mutex and read config again:
- `biometric_capture` re-reads `self_serve` and `self_serve_biometric_capture_timeout` to decide the capture plan/timeout [3](#0-2) .
- `verify_user_qr_code` re-reads `user_qr_validation_use_full_operator_qr` and `user_qr_validation_use_only_operator_location` to decide how strictly to validate the user's QR against the operator's identity/location [4](#0-3) .
- The enrollment decision path re-reads `ignore_user_centric_signups` from config to decide whether to trust a "user-centric" signup or force a full enrollment request [5](#0-4) .

Because `Config` can be replaced wholesale by a background download at any time (`Config::download_and_store` swaps the entire `Config` behind the same `Mutex`) [6](#0-5) , and because there is no per-signup snapshot that is threaded through consistently, a config change landing between these reads means the `self_serve` value used to pick the capture timeout can differ from the `self_serve` value used earlier in `do_signup`, and the QR-validation strictness (`user_qr_validation_use_only_operator_location`) or the enrollment-trust flag (`ignore_user_centric_signups`) used near the end of the signup can differ from what was in effect when the QR was actually scanned and validated.

### Impact Explanation
This mirrors the reported bug's root cause: a security-relevant, backend-mutable parameter is not pinned/snapshotted for the duration of a single logical operation, so different stages of that operation can be evaluated against different values. In the orb-core context this can weaken identity binding and fraud enforcement within a single signup — e.g., the operator/user QR relationship being validated under one location/full-QR strictness setting while the final enrollment decision (`ignore_user_centric_signups`, `self_serve`) is made under a different setting fetched moments later, or the biometric capture timeout no longer matching the `self_serve` mode that was actually used to gate age-verification (`self_serve_ask_op_qr_for_possibly_underaged`). The practical severity depends heavily on how frequently/asynchronously the backend config is refreshed during a signup and cannot be fully confirmed from static reading of the flow; this is a design weakness that could open a window for cross-signup state bleed/inconsistent enforcement, not a proven, easily-triggerable exploit.

### Likelihood Explanation
Low-to-Medium. Triggering it requires a backend config change to land in the small window between two config reads within one signup, which is timing-dependent and outside the attacking user's direct control (though an operator with backend config write access, or a race with a scheduled config refresh, could exploit it). The lack of any snapshot-and-thread-through-signup pattern means the window exists on every signup, but exploiting it deterministically for a specific bypass requires additional control over backend config timing that could not be fully verified in this review.

### Recommendation
Snapshot the relevant `Config` fields once at the start of `do_signup` (as is already partially done at line 497) and thread that single snapshot through all sub-routines of that signup (`biometric_capture`, `verify_user_qr_code`, enrollment decision, etc.) instead of having each function independently re-lock `orb.config`. This guarantees that a single signup is evaluated against one consistent, internally coherent configuration for its entire lifetime, eliminating the possibility of mixed old/new settings within one signup — directly analogous to the recommended fix of pinning the fee rate at loan-creation time rather than re-reading it at redemption time.

### Proof of Concept
Not independently verifiable without live backend control over config timing; the code paths cited above demonstrate that `orb.config.lock().await` is called at least four separate times within a single signup's control flow (`plans/mod.rs` lines 497-506, 639, 1167-1168, 1588-1592), each of which can observe a different in-memory `Config` value if a backend-initiated config refresh (`Config::download_and_store`, `src/config.rs` lines 357-368) completes between them.

### Citations

**File:** src/bin/orb-core.rs (L52-58)
```rust
    let config = if let Some(path) = &cli.config {
        serde_json::from_str(&fs::read_to_string(path).await?)?
    } else {
        Config::load_or_default().await
    };
    let config = Arc::new(Mutex::new(config));
    config.lock().await.propagate_to_ui(&ui);
```

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

**File:** src/plans/mod.rs (L639-646)
```rust
        let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
        {
            debug_report.enrollment_status(match signup_reason {
                SignupReason::Normal => enroll_user::Status::Success,
                _ => enroll_user::Status::Error,
            });
            signup_reason == SignupReason::Normal
        } else {
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

**File:** src/plans/mod.rs (L1588-1598)
```rust
        let Config {
            user_qr_validation_use_full_operator_qr,
            user_qr_validation_use_only_operator_location,
            ..
        } = *orb.config.lock().await;
        match backend::user_status::request(
            user_qr_code,
            operator_data,
            user_qr_validation_use_full_operator_qr,
            user_qr_validation_use_only_operator_location,
        )
```

**File:** src/config.rs (L354-368)
```rust
    /// Downloads the latest configuration from the backend, updates the shared
    /// configuration object, and stores the updated configuration to the file
    /// system.
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
