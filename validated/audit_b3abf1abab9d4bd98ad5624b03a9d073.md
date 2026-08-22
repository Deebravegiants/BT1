### Title
`MasterPlan::detect_fraud` unconditionally returns `Ok(false)`, bypassing all biometric fraud detection - ([File: src/plans/mod.rs])

### Summary
`MasterPlan::detect_fraud` is called after every successful `biometric_capture`/`biometric_pipeline` run to decide whether a signup should be flagged as fraudulent, but grep confirms the function body contains only `Ok(false) // FOSS: WE HAVE DELETED ALL FRAUD CHECKS` and never inspects the `pipeline` argument passed to it. This means the fraud-verdict fail-closed invariant is structurally violated: no biometric evidence (occlusion, face-identifier mismatch, liveness/replay indicators) can ever cause a signup to be marked as fraud.

### Finding Description
The call chain is `MasterPlan::do_signup` → `self.biometric_pipeline(orb, debug_report, &capture)` → `self.detect_fraud(orb, debug_report, pipeline.as_ref())`, as seen at: [1](#0-0) 

The result of `detect_fraud` directly determines `fraud_detected`, which feeds into `signup_reason` (`SignupReason::Fraud` vs `SignupReason::Normal`), which in turn governs `build_pcp`, `enroll_user`, and ultimately whether the signup is reported as successful via `report_signup_reason`. If `detect_fraud` always returns `Ok(false)` regardless of the contents of `pipeline` (occlusion errors, mismatched face-identifier fraud checks, or any other liveness/spoof signal computed by `biometric_pipeline`), then `fraud_detected` is always `false` and `SignupReason::Fraud` is unreachable through this path. A grep for the literal text `FOSS: WE HAVE DELETED ALL FRAUD CHECKS` and for `fn detect_fraud` both resolve to matches inside `src/plans/mod.rs`, corroborating that the function's body has been reduced to an unconditional `Ok(false)` that never reads `pipeline`.

Because there is no other fraud gate between `biometric_pipeline` and the credential/enrollment path (`build_pcp`, `enroll_user`), this is a fail-open bypass rather than a fail-closed check, violating the stated invariant that "liveness and fraud verdicts are fail-closed."

### Impact Explanation
Any unprivileged attacker who completes a normal QR scan and presents any face to the cameras — including an obviously spoofed or replayed presentation that would trip occlusion/liveness/face-identifier fraud checks — will never have their signup flagged as fraud through `detect_fraud`. This allows spoofed/fraudulent biometric captures to proceed to enrollment and credential issuance as if they were legitimate, undermining the core anti-fraud/anti-spoof guarantee of the Orb signup flow (biometric integrity / liveness bypass class of impact).

### Likelihood Explanation
Fully reachable by any user who can perform a signup session (present a QR code and a face to the cameras) — no privileged access, keys, or hardware tampering required. The precondition is simply that `biometric_capture` and `biometric_pipeline` complete (`pipeline` is `Some`), which happens on every normal capture attempt. This makes the bypass deterministic and repeatable on every signup.

### Recommendation
Restore the actual fraud-detection logic in `detect_fraud`: inspect the `pipeline: &biometric_pipeline::Pipeline` for occlusion status, face-identifier fraud-check mismatches, and other liveness/spoof indicators, and return `Ok(true)` (fraud detected) when any indicator fails, matching the fail-closed invariant. Add a regression test asserting that a `Pipeline` constructed with a known-fraudulent state (e.g., `Occlusion::Error`, mismatched face-identifier fraud checks) causes `detect_fraud` to return `true`.

### Proof of Concept
Unit test plan (to be added under `src/plans/fraud_check.rs` or `src/plans/mod.rs` tests):
1. Construct a dummy `biometric_pipeline::Pipeline` with `Occlusion::Error` and/or mismatched `face_identifier_fraud_checks` fields simulating an obviously spoofed/replayed presentation.
2. Call `MasterPlan::detect_fraud(orb, debug_report, Some(&pipeline))`.
3. Assert the result is currently `Ok(false)` (proving the bypass) — expected/fixed behavior should be `Ok(true)`.
4. Extend `do_signup` integration test to confirm `signup_reason` never becomes `SignupReason::Fraud` regardless of injected fraud indicators in `pipeline`, confirming the structural absence of enforcement described above. [1](#0-0)

### Citations

**File:** src/plans/mod.rs (L562-571)
```rust
        let pipeline = Box::pin(self.biometric_pipeline(orb, debug_report, &capture)).await?;
        let fraud_detected = !self.skip_fraud_checks()
            && self.detect_fraud(orb, debug_report, pipeline.as_ref()).await?;
        let signup_reason = if pipeline.is_none() {
            SignupReason::Failure
        } else if fraud_detected {
            SignupReason::Fraud
        } else {
            SignupReason::Normal
        };
```
