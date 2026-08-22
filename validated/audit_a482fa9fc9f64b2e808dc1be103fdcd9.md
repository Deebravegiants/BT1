### Title
Iris pipeline lacks liveness/plausibility validation, allowing spoofed iris captures (printed photo/patterned contact lens) to be committed as genuine iris code shares - ([File: src/agents/python/iris/mod.rs])

### Finding Description
`EstimateOutput::try_from(PipelineOutput)` only checks whether `output.iris_template` is `Some`/`None` and whether `output.error` is populated; if a template is present it unconditionally base64-decodes `iris_codes`/`mask_codes` via `IrisCodeArray::from_base64` and commits them via `GaloisRingIrisCodeShare::encode_iris_code`/`encode_mask_code`, with **no structural or biological-plausibility validation** (mask coverage ratio, entropy, occlusion thresholds, etc.) at this stage. [1](#0-0) 

Upstream, the only gating before an iris image reaches the pipeline is IR-Net's image-quality/geometry checks (`sharpness`, `occlusion_30/90`, `eye_opened`, `iris_aligned`, `gaze_valid`, `valid_for_identification`) used purely to select a "sharp" capture frame in `biometric_capture`, none of which are liveness/anti-spoof checks — they validate image clarity/geometry, not that the eye is a live human eye rather than a printed photo or patterned contact lens. [2](#0-1) 

Critically, the downstream fraud-detection stage that would normally catch such spoofing is a stub that always returns no fraud detected: `detect_fraud` in the master signup plan explicitly notes "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" and unconditionally returns `Ok(false)`. [3](#0-2) 

Consistently, `fraud_check.rs`'s `Report` type has empty check arrays (`fraud_checks`, `enabled_checks_from_config`, `feedback_messages`), so `fraud_detected()`/`fraud_detected_with_config()` can never signal fraud in this codebase, and `FraudChecks::run` returns an empty `Report` unconditionally. [4](#0-3) 

Because of this, once a well-formed base64 iris template survives `IrisCodeArray::from_base64` (any valid base64 blob decodes into a fixed-size bit array — no entropy/coverage validation is imposed), `EstimateOutput.iris_code_shares`/`mask_code_shares` are populated and flow directly into the biometric pipeline's `EyePipeline` and ultimately into `personal_custody_package::Pipeline`'s `iris_codes.json`/`iris_code_shares_*.json` as genuine biometric commitments. [5](#0-4) [6](#0-5) 

### Impact Explanation
An attacker presenting a printed iris photo or a patterned/printed contact lens during their own signup session can, provided the fake pattern is sharp/well-aligned enough to pass IR-Net's pure image-quality gates, get a fabricated `iris_template` accepted by `EstimateOutput::try_from`, with the resulting iris code shares committed into the custody package pipeline and uploaded as though captured from a genuine live iris. This breaks the invariant that iris-code commitments reflect genuine live capture, and corresponds to a liveness/fraud-bypass class of impact — fraudulent iris code enters the custody/enrollment pipeline as an authentic biometric signal.

### Likelihood Explanation
No privileged access, tampering, or social engineering is required — the attacker only needs to control the scene presented to the orb's own cameras during a normal, self-initiated signup. The only barrier is producing an artifact realistic enough to pass IR-Net's sharpness/occlusion/alignment thresholds (an image-quality bar, not a liveness bar). Since the fraud-detection stage is stubbed out to always report no fraud in this codebase (`detect_fraud` / `fraud_check.rs`), there is no secondary defense once an image-quality-passing spoof is captured, making the path fully reachable and repeatable across signup attempts.

### Recommendation
Reintroduce or wire in a genuine liveness/anti-spoof check (e.g., pupillary response, thermal signature, texture/frequency-domain anti-spoofing, or hardware-based liveness cues already partially scaffolded via `pupil_contraction` extension) as a hard gate before `EstimateOutput::try_from` commits an iris template, and populate `fraud_check.rs`'s `Report::fraud_checks`/`enabled_checks_from_config`/`feedback_messages` with real checks instead of leaving them as empty stubs. At minimum, add structural plausibility validation (mask coverage ratio bounds, iris-code entropy/self-similarity checks) inside `TryFrom<PipelineOutput> for EstimateOutput` to reject implausible templates before they are encoded into Galois ring shares.

### Proof of Concept
Fuzz/unit test plan for `src/agents/python/iris/mod.rs`:
1. Construct a `PipelineOutput` with `error: None` and an `iris_template` whose `iris_codes`/`mask_codes` are adversarially crafted but structurally valid base64 (e.g., all-`FF` runs simulating a low-entropy printed pattern, as already present in the existing test fixture `EXAMPLE_IRIS_OUTPUT` in `extracts.rs`). [7](#0-6) 
2. Call `TryFrom<PipelineOutput>::try_into::<EstimateOutput>()` and assert it returns `Ok(_)` regardless of mask coverage ratio/entropy of the crafted codes — demonstrating no structural rejection occurs.
3. Assert `output.iris_code_shares`/`mask_code_shares` are non-empty valid base64 Galois-ring shares derived directly from the adversarial input, confirming they would be committed into `personal_custody_package::Pipeline::make_iris_codes_json`/`make_iris_code_shares_jsons` unchanged.
4. Separately confirm `plans::mod::detect_fraud` returns `Ok(false)` unconditionally for any `Some(pipeline)` input, proving no downstream fraud gate exists to catch the crafted template.

### Citations

**File:** src/agents/python/iris/mod.rs (L99-131)
```rust
impl TryFrom<PipelineOutput> for EstimateOutput {
    type Error = PyError;

    fn try_from(output: PipelineOutput) -> std::result::Result<Self, Self::Error> {
        if let Some(iris_template) = output.iris_template {
            let iris_code = IrisCodeArray::from_base64(&iris_template.iris_codes)?;
            let mask_code = IrisCodeArray::from_base64(&iris_template.mask_codes)?;

            let iris_code_shares = GaloisRingIrisCodeShare::encode_iris_code(
                &iris_code,
                &mask_code,
                &mut rand::thread_rng(),
            )
            .map(|x| x.to_base64());
            let mask_code_shares =
                GaloisRingIrisCodeShare::encode_mask_code(&mask_code, &mut rand::thread_rng())
                    .map(|x| x.to_base64());

            Ok(EstimateOutput {
                iris_code_shares,
                mask_code_shares,
                iris_code: iris_template.iris_codes,
                mask_code: iris_template.mask_codes,
                iris_code_version: iris_template.iris_code_version,
                metadata: output.metadata,
                normalized_image: output.normalized_image,
                normalized_image_resized: output.normalized_image_resized,
            })
        } else {
            Err(output.error.expect("error not to be None"))
        }
    }
}
```

**File:** src/plans/biometric_capture/mod.rs (L238-259)
```rust
                let frame = frame.expect("frame must be set for an estimate output");
                let valid_capture = estimate.score >= IRIS_SCORE_MIN
                    && (!orb.ir_auto_exposure.is_enabled()
                        || IRIS_BRIGHTNESS_RANGE.contains(&frame.mean()))
                    && self.valid_capture_after <= Instant::now();

                if valid_capture {
                    let slot =
                        if self.target_left_eye { &mut self.left_ir } else { &mut self.right_ir };
                    if slot.is_none() {
                        dd_incr!(
                            "main.count.signup.during.biometric_capture.\
                             first_side_sharp_iris_detected",
                            &format!(
                                "side:{}",
                                if self.target_left_eye { "left" } else { "right" }
                            )
                        );
                    }
                    tracing::debug!("Found sharp iris: {}", estimate.score);
                    *slot = Some(FrameInfoIr::new(estimate, frame));
                }
```

**File:** src/plans/mod.rs (L1390-1406)
```rust
    /// Performs the fraud checks.
    #[allow(clippy::too_many_lines)]
    async fn detect_fraud(
        &mut self,
        orb: &mut Orb,
        _debug_report: &mut debug_report::Builder,
        pipeline: Option<&biometric_pipeline::Pipeline>,
    ) -> Result<bool> {
        orb.set_phase("Fraud detection").await;
        let Some(_pipeline) = pipeline else {
            return Ok(false);
        };

        // FOSS: WE HAVE DELETED ALL FRAUD CHECKS

        Ok(false)
    }
```

**File:** src/plans/fraud_check.rs (L64-153)
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

    /// Get the || result of all fraud checks, but under the Orb configuration.
    /// The end result might be different from the || of all fraud booleans as
    /// we might decide to not block a signup even if it's fraudulent.
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

    /// If any fraud check fails or is missing data, fraud is reported.
    #[must_use]
    pub fn fraud_detected(&self) -> bool {
        self.fraud_checks_strict().iter().any(|&v| v)
    }

    /// Report fraud checks as Datadog tags.
    pub fn as_datadog_tags(&self) -> impl Iterator<Item = String> {
        Self::DATADOG_TAGS.iter().zip(self.fraud_checks()).map(|(tag, res)| {
            format!("{}{}", tag, res.map_or("none".to_owned(), |b| b.to_string()))
        })
    }

    /// Report fraud checks as Datadog tags, but exclude reports of any fraud
    /// check that is not enabled in config.
    pub fn as_datadog_tags_with_config(
        &self,
        config: &BackendConfig,
    ) -> impl Iterator<Item = String> {
        self.as_datadog_tags()
            .zip(Self::enabled_checks_from_config(config))
            .filter_map(|(tag, is_enabled)| is_enabled.then_some(tag))
    }
}

/// Fraud checks plan.
#[derive(Debug)]
pub struct FraudChecks<'a> {
    _phantom: PhantomData<&'a ()>,
}

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
}
```

**File:** src/plans/biometric_pipeline/mod.rs (L350-376)
```rust
                        mega_agent_one::Output::Iris(iris::Output::Estimate(
                            iris::EstimateOutput {
                                iris_code_shares,
                                mask_code_shares,
                                iris_code,
                                mask_code,
                                iris_code_version,
                                metadata,
                                normalized_image,
                                normalized_image_resized,
                            },
                        )) => {
                            iris_left = Some(EyePipeline {
                                iris_code_shares,
                                mask_code_shares,
                                iris_code,
                                mask_code,
                                iris_code_version,
                                metadata,
                                iris_normalized_image: normalized_image,
                                iris_normalized_image_resized: normalized_image_resized,
                            });

                            self.set_timeout();
                            progress += IRIS_ESTIMATE_PROGRESS;
                        }
                        mega_agent_one::Output::Iris(iris::Output::Version(version)) => {
```

**File:** src/plans/personal_custody_package.rs (L568-581)
```rust
    fn make_iris_codes_json(&self, hashes: &mut BTreeMap<String, Digest>) -> Result<Vec<u8>> {
        let iris_codes = IrisCodesJson {
            iris_version: self.pipeline.iris_version.as_deref(),
            left_iris_code: self.pipeline.left_iris_code.as_deref(),
            left_mask_code: self.pipeline.left_mask_code.as_deref(),
            right_iris_code: self.pipeline.right_iris_code.as_deref(),
            right_mask_code: self.pipeline.right_mask_code.as_deref(),
        };
        let json = serde_json::to_string(&SerializeWithSortedKeys(&iris_codes))
            .wrap_err("serializing IrisCodesJson as json")?
            .into_bytes();
        hashes.insert("iris_codes.json".to_owned(), digest(&SHA256, &json));
        Ok(json)
    }
```

**File:** src/agents/python/iris/extracts.rs (L9-35)
```rust
    const EXAMPLE_IRIS_OUTPUT: &str = r"{
    'error': None,
    'normalized_image': None,
    'normalized_image_resized': None,
    'iris_template': {'iris_codes': 'E0zFXyJgq2+/sTFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF ... (truncated)
                      'mask_codes': '///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8zMzM/////////////////////////////////////////////////////////////////////////////////////////////////////////8zP/zMzAAAAAAA ... (truncated)
                      'iris_code_version': '1.7.2'},
    'metadata': {'eye_centers': {'iris_center': (564.8768229058003,
                                                 398.9210807004433),
                                 'pupil_center': (578.7788155676323,
                                                  401.6670096215058)},
                 'eye_orientation': 0.007373233121502842,
                 'eye_side': 'left',
                 'image_size': (1440, 1080),
                 'iris_bbox': {'x_max': 877.7410888671875,
                               'x_min': 254.19358825683594,
                               'y_max': 705.7726440429688,
                               'y_min': 93.87154388427734},
                 'iris_version': '1.5.1',
                 'occlusion30': 0.9950829028434285,
                 'occlusion90': 0.8284294618143734,
                 'ellipticity': {'pupil_ellipticity': 0.04, 'iris_ellipticity': 0.04},
                 'offgaze_score': 0.18155832771958066,
                 'pupil_to_iris_property': {'pupil_to_iris_center_dist_ratio': 0.04516609061229463,
                                            'pupil_to_iris_diameter_ratio': 0.388149379214243},
                 'template_property': {'visible_ratio': 0.78390625, 'lower_visible_ratio': 1.0, 'upper_visible_ratio': 0.5678125, 'abnormal_mask_ratio': 0.0215625, 'weighted_abnormal_mask_ratio': 0.021731390308341404, 'maskcode_hist': None}}
    }";
```
