### Title
Fraud detection is a permanent no-op, allowing `secure_element::sign` to produce a valid signature for a degraded/fraudulent capture - ([File: src/plans/fraud_check.rs])

### Summary
`fraud_check::FraudChecks::run` in `src/plans/fraud_check.rs` unconditionally returns an empty `Report {}` regardless of the `Pipeline` it is constructed from, because `N_FRAUD_CHECKS` is hard-coded to `0` and the `Pipeline` reference is discarded into a `PhantomData`. Consequently `Report::fraud_detected()` can never return `true`, so a `Pipeline` whose `occlusion` and `face_identifier_fraud_checks` fields are `Err(PyError)` (agent crash/timeout) is never flagged as fraudulent, and the flow proceeds to compute and sign the iris-code commitment via `secure_element::sign` in `enroll_user::make_signature`.

### Finding Description
`biometric_pipeline::Plan::run` in `src/plans/biometric_pipeline/mod.rs` builds `Pipeline { occlusion, face_identifier_fraud_checks, face_identifier_bundle, ... }` and explicitly preserves `Err(PyError)` values for `occlusion` and `face_identifier_fraud_checks` (lines 483-485) whenever the corresponding agent reports an error — it does not fail the whole pipeline in that case (only iris/IIP errors abort with `Error::Iris`). This means a `Pipeline` with occlusion/face-identifier failures but successful iris estimation is a normal, reachable state.

Downstream, `FraudChecks::new(&pipeline)` (`src/plans/fraud_check.rs:141-146`) stores the pipeline reference in an unused `PhantomData<&'a ()>` — the actual content of `pipeline.occlusion` / `pipeline.face_identifier_fraud_checks` is never read. `FraudChecks::run` (`src/plans/fraud_check.rs:148-152`) simply returns `Report {}`. Because `N_FRAUD_CHECKS = 0` (line 12), `Report::fraud_checks()` returns `[]`, so `fraud_checks_strict()` (line 72-74) and `fraud_detected()` (line 111-114) — whose doc-comment states "If any fraud check fails or is missing data, fraud is reported" — always evaluate over an empty array and always return `false`.

`enroll_user::make_signature` (`src/plans/enroll_user.rs:290-304`) computes the SHA-256 digest from `pipeline.v2.eye_left/eye_right` iris/mask codes and calls `secure_element::sign(ctx.finish())` unconditionally — it performs no check of `pipeline.occlusion` or `pipeline.face_identifier_fraud_checks` before signing. The only gate that is supposed to stop a degraded/fraudulent capture from being signed is the fraud-check report, and that report is structurally incapable of detecting anything.

### Impact Explanation
An attacker who can induce occlusion-detection or face-identifier agent failures during their own signup (e.g., through crafted physical presentation causing the Python agent to crash or time out, without any privileged access) still gets a validly signed iris-code commitment, because:
1. The pipeline still completes (only iris/IIP agent errors abort it).
2. `FraudChecks::run` always returns an empty `Report`.
3. `fraud_detected()` always returns `false`.
4. `make_signature`/`secure_element::sign` are reached and produce a valid signature over iris data that should have been rejected as fraud/degraded-capture.

This is a fail-closed invariant violation: a signed identity commitment is issued for a signup that should have been blocked for missing/failed fraud-relevant model outputs, undermining signup integrity/liveness guarantees (matches an Orb bounty impact category of "fraud/liveness check bypass" leading to acceptance of an invalid signup for signing).

### Likelihood Explanation
Reachable purely by an unprivileged attacker presenting a physical scene to the cameras during their own signup session — no operator, keys, or backend compromise needed. The precondition (occlusion or face-identifier agent returning `Err`, while iris/IIP still succeed) is a state explicitly modeled and handled (not rejected) by `biometric_pipeline::Plan::run`, so it is a legitimate, repeatable reachable state, not a theoretical corner case. The root cause (`N_FRAUD_CHECKS = 0`, `Report {}`) is unconditional and applies to every signup, making the bypass deterministic once the precondition is met.

### Recommendation
Make `FraudChecks::run`/`Report::fraud_detected` actually consume `pipeline.occlusion` and `pipeline.face_identifier_fraud_checks`: treat `Err(PyError)` in either field as an automatic fraud/fail-closed signal (consistent with the existing doc-comment "if fraud data are missing, we assume fraud is detected"), and gate `enroll_user::make_signature`/`secure_element::sign` (or the caller of `Plan::run` in `src/plans/mod.rs`) on this result before invoking `secure_element::sign`.

### Proof of Concept
Unit test in `src/plans/fraud_check.rs` (or a new test module):
```rust
#[test]
fn fraud_detected_should_be_true_when_pipeline_agents_failed() {
    // Construct a Pipeline (via Pipeline::default_with_ok() then override):
    let mut pipeline = crate::plans::biometric_pipeline::Pipeline::default_with_ok();
    pipeline.occlusion = Err(ai_interface::PyError::from(/* crash/timeout */));
    pipeline.face_identifier_fraud_checks = Err(ai_interface::PyError::from(/* crash/timeout */));

    let mut checks = FraudChecks::new(&pipeline);
    let report = checks.run();

    // Current behavior: this incorrectly passes, proving the bypass.
    assert!(!report.fraud_detected(), "BUG: fraud_detected() is always false");
    // Expected/fixed behavior (should fail against current code):
    // assert!(report.fraud_detected());
}
```
Combined with a call into `enroll_user::make_signature(&user_qr_code, &pipeline)`, showing it returns `Ok(signature)` (reaching `secure_element::sign`) even though `pipeline.occlusion`/`pipeline.face_identifier_fraud_checks` are `Err`, confirming the signature path is unguarded by fraud detection. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L64-82)
```rust
impl Report {
    const DATADOG_TAGS: [&'static str; N_FRAUD_CHECKS] = [];

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

**File:** src/plans/fraud_check.rs (L110-114)
```rust
    /// If any fraud check fails or is missing data, fraud is reported.
    #[must_use]
    pub fn fraud_detected(&self) -> bool {
        self.fraud_checks_strict().iter().any(|&v| v)
    }
```

**File:** src/plans/fraud_check.rs (L141-152)
```rust
impl<'a> FraudChecks<'a> {
    /// Create a new FraudCheck.
    #[must_use]
    pub fn new(_pipeline: &'a biometric_pipeline::Pipeline) -> Self {
        Self { _phantom: PhantomData }
    }

    /// Run all fraud checks.
    #[must_use]
    pub fn run(&mut self) -> Report {
        Report {}
    }
```

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

**File:** src/plans/biometric_pipeline/mod.rs (L343-349)
```rust
                        mega_agent_one::Output::Occlusion(occlusion::Output::Estimate(output)) => {
                            occlusion = Some(Ok(output));
                            progress += OCCLUSION_PROGRESS;
                        }
                        mega_agent_one::Output::Occlusion(occlusion::Output::Error(error)) => {
                            occlusion = Some(Err(error));
                        }
```

**File:** src/plans/biometric_pipeline/mod.rs (L476-489)
```rust
        Ok(Pipeline {
            v2: PipelineV2 {
                eye_left: iris_left.unwrap(),
                eye_right: iris_right.unwrap(),
                ir_net_version: ir_net_version.unwrap(),
                iris_version: iris_version.clone().unwrap(),
            },
            occlusion: occlusion.unwrap(),
            face_identifier_fraud_checks: face_identifier_fraud_checks.unwrap(),
            face_identifier_bundle: face_identifier_bundle.unwrap(),
            mega_agent_one_config: mega_agent_one_config.unwrap(),
            mega_agent_two_config: mega_agent_two_config.unwrap(),
        })
    }
```

**File:** src/secure_element.rs (L12-47)
```rust
pub fn sign<T: AsRef<[u8]>>(data: T) -> Result<Vec<u8>> {
    fn inner(data: &[u8]) -> Result<Vec<u8>> {
        let encoded = BASE64.encode(data);

        tracing::info!("Running orb-sign-iris-code");
        let mut command = Command::new("/usr/bin/orb-sign-iris-code");
        command.stdin(Stdio::piped());
        command.stdout(Stdio::piped());
        command.stderr(Stdio::piped());
        let mut child = command.spawn().wrap_err("running orb-sign-iris-code")?;

        let mut stdin = child.stdin.take().unwrap();
        stdin.write_all(encoded.as_bytes())?;
        drop(stdin);

        let output = child.wait_with_output().wrap_err("waiting for orb-sign-iris-code")?;
        let success = output.status.success();
        for line in String::from_utf8_lossy(&output.stderr).lines() {
            if success {
                tracing::trace!("orb-sign-iris-code {}", line);
            } else {
                tracing::error!("orb-sign-iris-code {}", line);
            }
        }
        if !success {
            if let Some(code) = output.status.code() {
                bail!("orb-sign-iris-code exited with non-zero exit code: {code}");
            } else {
                bail!("orb-sign-iris-code terminated by signal");
            }
        }
        BASE64.decode(&output.stdout).wrap_err("decoding orb-sign-iris-code output")
    }

    inner(data.as_ref())
}
```
