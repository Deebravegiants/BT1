### Title
Face-identifier model exceptions are stored as `Err` in `Pipeline` but do not abort signup, letting fraud/liveness verdicts be silently skipped - (File: `src/plans/biometric_pipeline/mod.rs`)

### Summary
When the Python face-identifier model throws (e.g. from an occluded, edge-of-frame, or corrupted RGB scene), `Environment::iterate` returns `face_identifier::Output::Error(...)`, and `Plan::run` in `src/plans/biometric_pipeline/mod.rs` stores this as `face_identifier_fraud_checks = Some(Err(error.clone()))` rather than aborting the pipeline. The function then proceeds to build the full `Pipeline` struct, including completed iris estimates, with this field left as `Err`, instead of failing the loop or returning an early error the way iris errors are handled.

### Finding Description
Inside `Plan::run`'s main polling loop, `face_identifier::Output::Error(error)` sets: [1](#0-0) 
This differs sharply from the handling of iris errors in the same loop, where `iris::Output::Error(error)` immediately does `return Err(Error::Iris(error))?;`, aborting the whole pipeline run: [2](#0-1) 
Because the face-identifier error is captured as `Some(Err(...))` (not `None`), it satisfies the loop's exit condition `face_identifier_fraud_checks.is_none()` just like a success would, so the `while` loop terminates normally and falls through to constructing the `Pipeline`: [3](#0-2) [4](#0-3) 
The `Pipeline` is returned as `Ok(Pipeline { ..., face_identifier_fraud_checks: face_identifier_fraud_checks.unwrap(), ... })` — the `.unwrap()` only unwraps the `Option`, not the inner `Result`, so an `Err(PyError)` value is a completely valid, non-panicking path into a successfully-returned `Pipeline`. This means a scene that reliably crashes/throws in the face-identifier model (extreme occlusion, edge-of-frame face, corrupted RGB frame feeding the Python model) can produce a `Pipeline` whose fraud/liveness field is `Err` while iris capture, mega-agent configs, and the rest of the biometric pipeline complete normally, with no distinguishing "hard fail" for this specific error class inside `biometric_pipeline::Plan::run`.

### Impact Explanation
Fraud/liveness detection is a fail-closed safety control: `Output::Error` must be treated as "deny" to prevent unvetted or fraudulent face data from progressing toward iris capture and identity-binding/signup completion. By instead encoding it as `Err` inside a successfully-constructed `Pipeline` (rather than aborting `Plan::run` the way iris errors do), the pipeline’s completion path treats "no verdict" the same as "verdict pending success," deferring the fail-closed decision to whatever later consumes `Pipeline.face_identifier_fraud_checks`. This matches the "liveness/fraud verdict bypass" impact category — a signup can proceed further into biometric processing on the strength of an attacker-influenced camera scene that merely needs to make the Python model throw, rather than needing to actually pass the fraud check.

### Likelihood Explanation
The precondition is attacker-controllable purely through the camera scene during the attacker's own signup session (occlusion, positioning at the frame edge, or a corrupted/malformed RGB frame) — no privileged access, keys, or social engineering required, consistent with the allowed threat model. Forcing a specific model exception deterministically may take experimentation, but the code path itself imposes no barrier: any `face_identifier::Output::Error` unconditionally takes the `Err(error.clone())` branch and lets the loop complete.

### Recommendation
Handle `face_identifier::Output::Error` the same way iris errors are handled: `return Err(Error::FaceIdentifier(error))?;` (or an equivalent immediate abort) inside `Plan::run`, rather than storing it as `Some(Err(...))` and letting pipeline construction succeed. If downstream consumers must be able to distinguish this error for reporting, an early abort with a typed error variant should be used instead of embedding the error into a value treated as "present" for loop-exit purposes.

### Proof of Concept
Unit/integration test plan for `src/plans/biometric_pipeline/mod.rs`:
1. Mock/stub the face-identifier agent so it emits `face_identifier::Output::Error(PyError{..})` for the fraud-check estimate while iris/occlusion/mega-agent outputs succeed normally.
2. Run `biometric_pipeline::Plan::run` (or a reduced harness replicating the loop) and assert it returns `Err(_)` (aborts), not `Ok(Pipeline{ face_identifier_fraud_checks: Err(_), .. })`.
3. As currently written, the test would show `Plan::run` returning `Ok(Pipeline { face_identifier_fraud_checks: Err(error), .. })`, confirming the pipeline completes instead of failing closed — expected/fixed behavior is `Err` propagation out of `Plan::run` matching the iris-error precedent at lines 379–382.

### Citations

**File:** src/plans/biometric_pipeline/mod.rs (L308-317)
```rust
        while iris_version.is_none()
            || ir_net_version.is_none()
            || occlusion.is_none()
            || face_identifier_fraud_checks.is_none()
            || face_identifier_bundle.is_none()
            || mega_agent_one_config.is_none()
            || mega_agent_two_config.is_none()
            || iris_left.is_none()
            || iris_right.is_none()
        {
```

**File:** src/plans/biometric_pipeline/mod.rs (L326-329)
```rust
                    face_identifier::Output::Error(error) => {
                        face_identifier_fraud_checks = Some(Err(error.clone()));
                        face_identifier_bundle = Some(Err(error.clone()));
                    }
```

**File:** src/plans/biometric_pipeline/mod.rs (L379-382)
```rust
                        mega_agent_one::Output::Iris(
                            iris::Output::Error(error),
                            // If IIP or Iris fail, there is not much we can do.
                        ) => return Err(Error::Iris(error))?,
```

**File:** src/plans/biometric_pipeline/mod.rs (L476-488)
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
```
