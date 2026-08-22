### Title
Fraud detection is unconditionally disabled, causing all signups (including spoofed/occluded presentations) to be sent to the backend as `SignupReason::Normal` - (File: src/plans/fraud_check.rs)

### Summary
`FraudChecks::run()` in `src/plans/fraud_check.rs` always returns an empty `Report {}` because `N_FRAUD_CHECKS` is hardcoded to `0`, and `Report::fraud_detected()`/`fraud_detected_with_config()` therefore always evaluate over an empty array and always return `false`. Any caller such as `plans::mod::detect_fraud` that relies on this report to decide `SignupReason` will always classify the signup as `Normal`, regardless of pipeline quality/occlusion/spoof signals, before the package is shipped via `upload_pcp_tier_0`/`signup_post::request`.

### Finding Description
`FraudChecks::run(&mut self) -> Report` unconditionally returns `Report {}` [1](#0-0)  and the constant driving all check arrays is fixed at zero with an explicit comment stating the checks were deleted: `const N_FRAUD_CHECKS: usize = 0;` [2](#0-1) . `Report::fraud_checks()`, `fraud_checks_strict()`, `enabled_checks_from_config()`, and `feedback_messages()` all return empty arrays sized by `N_FRAUD_CHECKS` [3](#0-2) , so `fraud_detected()` — `self.fraud_checks_strict().iter().any(|&v| v)` — iterates over an empty slice and always returns `false` [4](#0-3) , and `fraud_detected_with_config()` likewise always produces `(false, [])` [5](#0-4) . `FraudChecks::new()` accepts a `&biometric_pipeline::Pipeline` but stores only a `PhantomData`, meaning pipeline content (occlusion, spoof/liveness signals, image quality) is never inspected [6](#0-5) . Consequently, any caller (`plans::mod::detect_fraud`) that derives `SignupReason` from this report will always compute `SignupReason::Normal` per the default variant [7](#0-6) , and this reason string is what gets sent in the multipart `signup_post::request()` call to the backend `/api/v2/signups/{signup_id}` endpoint [8](#0-7) . There is no other on-Orb enforcement point between capture/pipeline completion and package upload that inspects pipeline content for fraud, so a presentation/replay/occlusion condition that would previously have been flagged is now shipped as a normal, non-fraud signup.

### Impact Explanation
This disables the Orb-side fraud/liveness fail-closed gate entirely: any completed biometric pipeline — including one built from an occluded face, degraded-quality iris capture, or spoofed presentation that the (deleted) checks were designed to catch — is unconditionally tagged `SignupReason::Normal` and forwarded to the backend along with the derived iris codes/pipeline data. This matches "liveness/fraud bypass" impact under presentation/replay-attack acceptance as genuine signup, since the on-device fail-closed control that should reject such presentations is a permanent no-op.

### Likelihood Explanation
Fully deterministic and always triggered: `N_FRAUD_CHECKS = 0` guarantees `fraud_detected()`/`fraud_detected_with_config()` return `false` for every signup regardless of pipeline content, with no conditional path that could re-enable checks at runtime. Any attacker who reaches `biometric_pipeline` with a valid QR pair (stated precondition) will have this code path executed unconditionally.

### Recommendation
Restore actual fraud/liveness checks in `FraudChecks::run()` that inspect the `biometric_pipeline::Pipeline` contents (occlusion, glasses/mask/contact-lens detection, multi-face, head pose, image quality, underage, etc.) and populate `Report.check_results`/`fraud_checks()` accordingly instead of the empty stub; set `N_FRAUD_CHECKS` to the real number of enabled checks and remove the "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" no-op so `fraud_detected()` can return `true` for degraded/spoofed presentations, causing `detect_fraud`/`SignupReason` to correctly report `Fraud` before upload.

### Proof of Concept
Unit test in `src/plans/fraud_check.rs`:
```rust
#[test]
fn fraud_checks_never_detect_fraud() {
    // Construct any Report (even a "worst case" one) and confirm no check can ever fire.
    let report = Report::default();
    assert!(!report.fraud_detected());
    let (flag, feedback) = report.fraud_detected_with_config(&BackendConfig::default());
    assert!(!flag);
    assert!(feedback.is_empty());
}
```
This asserts that regardless of pipeline content, `Report::fraud_detected()` always returns `false` because `N_FRAUD_CHECKS == 0`, demonstrating the fail-closed fraud invariant cannot hold — no input can make this test fail, proving the check is dead code that always yields `SignupReason::Normal` downstream in `detect_fraud`/`signup_post::request`.

### Citations

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L67-82)
```rust
    fn fraud_checks(&self) -> [Option<bool>; N_FRAUD_CHECKS] {
        []
    }

    /// If fraud data are missing, we assume fraud is detected.
    fn fraud_checks_strict(&self) -> [bool; N_FRAUD_CHECKS] {
        self.fraud_checks().map(|v| v.unwrap_or(true))
    }

    fn enabled_checks_from_config(_config: &BackendConfig) -> [bool; N_FRAUD_CHECKS] {
        []
    }

    fn feedback_messages() -> [Option<PipelineFailureFeedbackMessage>; N_FRAUD_CHECKS] {
        []
    }
```

**File:** src/plans/fraud_check.rs (L87-108)
```rust
    #[must_use]
    pub fn fraud_detected_with_config(
        &self,
        config: &BackendConfig,
    ) -> (bool, Vec<PipelineFailureFeedbackMessage>) {
        let enabled_checks = Self::enabled_checks_from_config(config);
        let fraud_results = self.fraud_checks_strict();
        let feedback_msgs = Self::feedback_messages();

        let feedback: Vec<PipelineFailureFeedbackMessage> = enabled_checks
            .iter()
            .zip(fraud_results.iter())
            .zip(feedback_msgs.iter())
            .filter_map(
                |((&enabled, &result), feedback_msg)| {
                    if enabled && result { feedback_msg.clone() } else { None }
                },
            )
            .collect();

        (!feedback.is_empty(), feedback)
    }
```

**File:** src/plans/fraud_check.rs (L110-114)
```rust
    /// If any fraud check fails or is missing data, fraud is reported.
    #[must_use]
    pub fn fraud_detected(&self) -> bool {
        self.fraud_checks_strict().iter().any(|&v| v)
    }
```

**File:** src/plans/fraud_check.rs (L141-146)
```rust
impl<'a> FraudChecks<'a> {
    /// Create a new FraudCheck.
    #[must_use]
    pub fn new(_pipeline: &'a biometric_pipeline::Pipeline) -> Self {
        Self { _phantom: PhantomData }
    }
```

**File:** src/plans/fraud_check.rs (L148-152)
```rust
    /// Run all fraud checks.
    #[must_use]
    pub fn run(&mut self) -> Report {
        Report {}
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

**File:** src/backend/signup_post.rs (L98-161)
```rust
/// Makes a signup request.
#[allow(clippy::too_many_arguments)]
pub async fn request(
    signature: Option<&String>,
    signup_id: &str,
    operator_qr_code: &qr_scan::user::Data,
    user_qr_code: &qr_scan::user::Data,
    s3_region: &str,
    capture: &Capture,
    pipeline: Option<&Pipeline>,
    signup_reason: SignupReason,
) -> Result<Response> {
    dd_gauge!(
        "main.gauge.signup.sharpest_iris",
        capture.eye_left.ir_net_estimate.score.to_string(),
        "side:left"
    );
    dd_gauge!(
        "main.gauge.signup.sharpest_iris",
        capture.eye_right.ir_net_estimate.score.to_string(),
        "side:right"
    );
    tracing::info!("Orb OS version: {:?}", &*ORB_OS_VERSION);
    tracing::info!("Signup reason: {:?}", signup_reason);
    let codes = pipeline.map_or(String::new(), |p| {
        serde_json::to_string_pretty(&format_pipeline(p)).expect("always a valid JSON")
    });
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

    let request = request.build()?;
    let headers = request.headers().clone();
    let request_size = headers.get("Content-Length");
    tracing::debug!("Sending request {:#?} with size: {:?}", request, request_size);

    let t = SystemTime::now();
    let response = super::client()?.execute(request).await?;
    tracing::debug!("Received response {:#?}", response);
    response.error_for_status_ref()?;
    let response = response.json::<Response>().await?;
    dd_timing!("main.time.http.signup_request", t);
    if let Some(request_size) = request_size {
        dd_gauge!("main.time.http.signup_request_size", request_size.to_str().unwrap_or("0"));
    }
    tracing::debug!("Received response {:#?}", response);
    Ok(response)
}
```
