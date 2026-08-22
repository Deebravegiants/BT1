### Title
Personal Custody Package (biometric) tier1/tier2 data is irreversibly uploaded to the backend before the signup/enrollment verdict is finalized, with no compensating deletion on fraud/failure - (File: `src/plans/mod.rs`)

### Summary
The Sherlock report describes a class of bug where an irreversible, real-world-costed action (the `withdraw()` gas refund) is bundled together with a later, attacker-influenceable step (`on_call()`), and when that later step fails, the whole atomic unit reverts, so the compensating/refund action never actually lands — draining the signer with no way to recover. The generalizable bug class is: *committing an irreversible side-effect based on an assumption that a downstream authorization/verification step will succeed, with no rollback or compensation path if it doesn't.*

`orb-core`'s signup flow contains an analogous pattern: encrypted biometric data (tier1/tier2 of the Personal Custody Package — normalized iris images/codes, iris code shares, face embeddings, face thumbnail) is uploaded to the backend fire-and-forget, unconditionally, before the enrollment/fraud verdict that determines whether the signup is actually valid is known.

### Finding Description
In `MasterPlan::do_signup` (`src/plans/mod.rs`), after biometric capture, pipeline processing and fraud detection, the plan builds the Personal Custody Package (`build_pcp`) and uploads "tier 0" synchronously with `upload_pcp_tier_0`, which is properly gated — if it fails, the function returns early: [1](#0-0) 

However, immediately afterward, for `pcp_version >= 3`, tier1 and tier2 (which contain the actual normalized iris images/codes, iris/mask code shares, and face identifier embeddings/thumbnail — see the package construction) are pushed to the `data_uploader` agent asynchronously and unconditionally, with no gating on the eventual result of enrollment or fraud detection: [2](#0-1) 

The `data_uploader` agent then uploads these tiers to the backend via presigned URLs, retrying indefinitely on network/server errors and only giving up on client errors — it has no concept of "cancel this upload because the signup was later rejected": [3](#0-2) 

Meanwhile, the actual decision of whether the signup is legitimate happens *after* this point, in `enroll_user`, which calls the backend to verify the signup and can return `SignupVerificationNotSuccessful`, `ServerError`, or `Error`: [4](#0-3) 

Fraud detection itself also happens before the PCP tiers are queued, and its outcome (`SignupReason::Fraud`) is only used to tag the metadata sent along with the enrollment call — it does not gate or retract the tier1/tier2 uploads that have already been queued for the same biometric data: [5](#0-4) 

There is no code path (visible via the async, fire-and-forget `Input::Pcp` queue and the retry-until-success `upload_pcp` loop) that deletes or invalidates tier1/tier2 data from the backend if the subsequent enrollment step returns `SignupVerificationNotSuccessful`, `ServerError`, or if fraud is later confirmed server-side. The irreversible action (uploading sensitive biometric material tied to a `signup_id`/`user_id`) is committed on the assumption that the downstream verification will succeed, exactly mirroring the SUI bug's root cause: a compensating/undo step is not actually coupled atomically to the outcome of the step it depends on.

### Impact Explanation
This results in biometric data (iris codes, iris code shares, face embeddings, face thumbnail) being retained on the backend for signups that:
- fail signup verification (duplicate detection, backend fraud detection, orb-detected fraud, backend legacy/inflight matches),
- fail due to a `ServerError` or network `Error` during enrollment,
- are cancelled/expired between PCP tier0 upload and the final poll result.

In all of these cases, the tier0 package upload is already gated by a success check, but tier1/tier2 (the biometric identifiers themselves) are not gated at all — they are uploaded regardless of whether the signup is ultimately accepted. This is a retention/disclosure of sensitive biometric data beyond the scope of an authorized/completed signup, which is explicitly an accepted impact category (biometric data disclosure/retention).

### Likelihood Explanation
This path is reachable by any unprivileged user undergoing a normal signup on an orb with `pcp_v3` enabled: causing repeated `SignupVerificationNotSuccessful`/`ServerError` outcomes (e.g. duplicate signup attempts, or triggering server-side fraud detection) is entirely within reach of a normal end user and does not require any privileged operator/node access. No malicious node/peer/hardware access is required — the trigger is simply a normal-looking signup attempt that the backend later rejects.

### Recommendation
Do not enqueue tier1/tier2 (or any biometric-identifying package tiers) for upload until the enrollment verdict (`enroll_user::Status::Success`) is known, or, if uploading earlier is required for latency reasons, add an explicit backend-side deletion/invalidation call tied to the final signup verdict so that biometric packages for rejected/failed/fraudulent signups are not retained. This mirrors the Sherlock report's mitigation of decoupling the irreversible action from the step whose success it depends on, and instead making the two steps properly atomic (or adding an explicit compensating action).

### Proof of Concept
1. A user completes biometric capture and pipeline processing on an orb running with `pcp_v3` enabled.
2. `build_pcp` succeeds and `upload_pcp_tier_0` succeeds, so the code proceeds past the early-return gate at `src/plans/mod.rs:599-612`.
3. Tier1 and tier2 packages (iris codes, iris code shares, normalized iris images, face embeddings/thumbnail) are sent to the `data_uploader` agent (`src/plans/mod.rs:613-636`) and begin uploading to the backend in the background.
4. `enroll_user::Plan::run` subsequently calls the backend and receives `success: false` (e.g. because the backend's own fraud/duplicate detection rejects the signup) — see `src/plans/enroll_user.rs:157-176` — returning `Status::SignupVerificationNotSuccessful`.
5. No code path deletes or invalidates the tier1/tier2 data already uploaded in step 3; the sensitive biometric package remains stored on the backend despite the signup being rejected.

Note: I could not fully verify from the index whether the backend itself performs any independent server-side deletion of rejected-signup PCP tiers (that logic, if any, would live outside `orb-core`); this analysis is scoped strictly to what `orb-core` does/does not do to gate or roll back these uploads.

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

**File:** src/plans/mod.rs (L599-612)
```rust
            data_uploader::wait_queues(orb.data_uploader.enabled().unwrap()).await?;
            if !self
                .upload_pcp_tier_0(
                    orb,
                    &result.signup_id,
                    &user_id,
                    packages.tier0,
                    packages.tier0_checksum,
                    if pcp_version >= 3 { Some(0) } else { None },
                )
                .await?
            {
                return Ok(result);
            }
```

**File:** src/plans/mod.rs (L613-636)
```rust
            if pcp_version >= 3 {
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id: user_id.clone(),
                        data: packages.tier1,
                        checksum: packages.tier1_checksum.as_ref().to_vec(),
                        tier: 1,
                    })))
                    .await?;
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id,
                        data: packages.tier2,
                        checksum: packages.tier2_checksum.as_ref().to_vec(),
                        tier: 2,
                    })))
                    .await?;
            }
```

**File:** src/agents/data_uploader.rs (L169-217)
```rust
impl Agent {
    async fn upload_pcp(&self, pcp: Pcp, id: u64) -> (u8, u64) {
        let Pcp { signup_id, user_id, data, checksum, tier } = pcp;
        tracing::info!(
            "Start uploading a personal custody package tier {tier} for signup_id={signup_id}"
        );
        let t = Instant::now();
        loop {
            let response = backend::upload_personal_custody_package::request(
                &signup_id,
                &user_id,
                checksum.as_ref(),
                &data,
                Some(tier),
                &self.config,
            )
            .await;
            match response {
                Ok(()) => {
                    dd_timing!("main.time.signup.upload_custody_images" + format!("t{}", tier), t);
                    tracing::info!(
                        "Personal custody package tier {tier} uploading completed in: {}ms",
                        t.elapsed().as_millis()
                    );
                    break;
                }
                Err(err) => {
                    tracing::error!("UPLOAD PERSONAL CUSTODY PACKAGE TIER {tier} ERROR: {err:?}");
                    dd_incr!(
                        "main.count.http.upload_custody_images.error.network_error",
                        "error_type:normal"
                    );
                    if let Some(reqwest_err) = err.downcast_ref::<reqwest::Error>() {
                        if let Some(status) = reqwest_err.status() {
                            if status.is_client_error() {
                                dd_incr!(
                                    "main.count.signup.result.failure.upload_custody_images",
                                    "type:network_error",
                                    "subtype:signup_request"
                                );
                                break;
                            }
                        }
                    }
                }
            }
        }
        (tier, id)
    }
```

**File:** src/plans/enroll_user.rs (L146-176)
```rust
                        match response {
                            Ok(signup_poll::Response {
                                success: true,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                tracing::info!("SIGNUP SUCCESS");
                                dd_incr!("main.count.http.user_enrollment.success.success_unique");
                                dd_incr!("main.count.http.user_enrollment.success.success");
                                return Status::Success;
                            }
                            Ok(signup_poll::Response {
                                success: false,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                // This includes the following cases:
                                //   1. Backend duplicates
                                //   2. Backend legacy signup requests
                                //   3. Backend inflight matches
                                //   4. Backend detected fraud
                                //   5. Orb agent, internal, capture or pipeline failures
                                //   6. Orb detected fraud
                                tracing::info!("SIGNUP FAIL");
                                dd_incr!("main.count.http.user_enrollment.success.failed");
                                dd_incr!(
                                    "main.count.signup.result.failure.user_enrollment",
                                    "type:failure"
                                );
                                return Status::SignupVerificationNotSuccessful;
                            }
```
