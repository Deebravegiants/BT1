### Title
Fraud-specific liveness/anti-spoofing failure reasons are disclosed one-to-one to the unprivileged signup app via `SignupEnded.failure_feedback` - (File: `src/debug_report.rs`)

### Summary
`Builder::failure_feedback_after_capture_proto` maps every `PipelineFailureFeedbackMessage` variant (including fraud-sensitive ones like `ContactLenses`, `Mask`, `MultipleFaces`, `Underaged`) to its own distinct `self_serve::orb::v1::signup_ended::FailureFeedbackType` i32 value, and returns that value directly to the app over Orb Relay. This directly contradicts the code comment stating the reasons are supposed to be collapsed into "a high level reason" so fraud-specific detail is not disclosed.

### Finding Description
In `Builder::failure_feedback_after_capture_proto` (`src/debug_report.rs`, ~lines 745-791), each `AfterCaptureFeedbackMessage::Pipeline(msg)` is matched exhaustively and translated 1:1 into the corresponding `FailureFeedbackType` variant: [1](#0-0) 

Despite the comment directly above this match block claiming "We don't disclose the full list of reasons because many of them relate to fraud. Instead this list only contains a high level reason which helps end-users troubleshoot," the implementation does the opposite: it preserves a distinct output code for every input variant (`ContactLenses`, `EyeGlasses`, `Mask`, `FaceOcclusion`, `MultipleFaces`, `EyesOcclusion`, `HeadPose`, `Underaged`, `LowImageQuality`) rather than collapsing them into a shared generic code. [2](#0-1) 

These `PipelineFailureFeedbackMessage` values originate from the fraud-check pipeline (`src/plans/fraud_check.rs`) and are pushed into `failure_feedback_after_capture` via `Builder::fraud_check_feedback_messages`: [3](#0-2) 

The resulting `Vec<i32>` is what ends up in `SignupEnded.failure_feedback` sent back to the app over Orb Relay for self-serve signups. Since each fraud-related heuristic (contact lenses, mask, multiple faces, underage, etc.) maps to a unique, always-emitted numeric code, an attacker running their own self-serve signup session can trivially distinguish which specific liveness/fraud check failed versus a purely benign image-quality issue, simply by observing the returned code. No aggregation, bucketing, or randomization is applied before transmission — the only post-processing is `sort_unstable`/`dedup` on the resulting vector, which does not obscure which specific variant(s) triggered. [4](#0-3) 

### Impact Explanation
An attacker in their own self-serve signup session (unprivileged, using only their own QR/device/scene) can iterate over presented physical conditions (e.g., wearing contact lenses, a mask, presenting multiple faces, spoofing to trigger `EyesOcclusion` vs `Mask` vs `MultipleFaces`) and use the distinct returned `FailureFeedbackType` code to determine precisely which fraud/liveness heuristic rejected them. This enables iterative tuning of a physical presentation attack (e.g., adjusting a mask, lens type, or occlusion) to find the exact configuration that evades a specific fraud check, undermining the intended containment of fraud signal detail from the party being screened. This matches an information-disclosure / fraud-signal-leak class of impact (aiding liveness/fraud bypass tuning) rather than a direct signup-authorization or biometric-secrecy breach.

### Likelihood Explanation
Highly likely and easily reproducible: this requires no privileges beyond running the self-serve signup flow as an ordinary user, repeated multiple times with different scene presentations, and observing the standard `SignupEnded` message fields that are already part of the intended app-facing protocol. No additional bypass of authentication, encryption, or backend logic is needed — the code path is reached on every normal capture failure.

### Recommendation
Collapse `PipelineFailureFeedbackMessage` variants into a small set of high-level, fraud-agnostic categories before assigning `FailureFeedbackType` in `failure_feedback_after_capture_proto`, consistent with the stated intent in the comment (e.g., map `ContactLenses`, `Mask`, `MultipleFaces`, `Underaged` to a single generic "FaceObstruction"/"Ineligible" type indistinguishable from benign quality issues), rather than doing a direct 1:1 enum-to-enum mapping.

### Proof of Concept
Differential unit test in `src/debug_report.rs`:
1. Construct a `Builder` and call `fraud_check_feedback_messages(&[PipelineFailureFeedbackMessage::Mask])`, call `failure_feedback_after_capture_proto()`, record code `A`.
2. Reset, call `fraud_check_feedback_messages(&[PipelineFailureFeedbackMessage::LowImageQuality])`, call `failure_feedback_after_capture_proto()`, record code `B`.
3. Repeat for `ContactLenses`, `MultipleFaces`, `Underaged`, `EyeGlasses`, `HeadPose`, `FaceOcclusion`, `EyesOcclusion`.
4. Assert: expected (per comment) — all fraud-sensitive variants should collapse to the same generic code as `LowImageQuality`. Actual — each produces a distinct i32 (`A != B` and all codes pairwise distinct), demonstrating the disclosure gap.

### Citations

**File:** src/debug_report.rs (L576-583)
```rust
    pub fn fraud_check_feedback_messages(
        &mut self,
        messages: &[PipelineFailureFeedbackMessage],
    ) -> &mut Self {
        self.failure_feedback_after_capture
            .extend(messages.iter().map(|msg| AfterCaptureFeedbackMessage::Pipeline(msg.clone())));
        self
    }
```

**File:** src/debug_report.rs (L751-753)
```rust
                // We don't disclose the full list of reasons because many of them relate to fraud.
                // Instead this list only contains a high level reason which helps end-users
                // troubleshoot.
```

**File:** src/debug_report.rs (L754-782)
```rust
                AfterCaptureFeedbackMessage::Pipeline(msg) => match msg {
                    PipelineFailureFeedbackMessage::ContactLenses => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::ContactLenses
                    }
                    PipelineFailureFeedbackMessage::EyeGlasses => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::EyeGlasses
                    }
                    PipelineFailureFeedbackMessage::Mask => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::Mask
                    }
                    PipelineFailureFeedbackMessage::FaceOcclusion => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::FaceOcclusion
                    }
                    PipelineFailureFeedbackMessage::MultipleFaces => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::MultipleFaces
                    }
                    PipelineFailureFeedbackMessage::EyesOcclusion => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::EyesOcclusion
                    }
                    PipelineFailureFeedbackMessage::HeadPose => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::HeadPose
                    }
                    PipelineFailureFeedbackMessage::Underaged => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::Underaged
                    }
                    PipelineFailureFeedbackMessage::LowImageQuality => {
                        self_serve::orb::v1::signup_ended::FailureFeedbackType::LowImageQuality
                    }
                },
```

**File:** src/debug_report.rs (L786-791)
```rust
            } as i32)
            .collect();
        messages.sort_unstable();
        messages.dedup();
        messages
    }
```
