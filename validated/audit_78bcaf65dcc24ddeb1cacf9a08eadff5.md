### Title
`TryFrom<PipelineOutput> for EstimateOutput` silently discards a populated `error` when `iris_template` is also present, violating fail-closed error handling - ([File: src/agents/python/iris/mod.rs])

### Finding Description
`PipelineOutput` (defined in `src/agents/python/iris/types.rs`) models the raw Python iris-pipeline response as two independent `Option` fields, `error: Option<PyError>` and `iris_template: Option<IrisTemplate>`, with no invariant enforced that they are mutually exclusive. [1](#0-0) 

The conversion `impl TryFrom<PipelineOutput> for EstimateOutput` only branches on `output.iris_template`: if it is `Some(..)`, the function unconditionally builds and returns a successful `EstimateOutput`, regardless of whether `output.error` is also `Some(..)`. The `error` field is only ever consulted in the `else` branch, i.e. only when `iris_template` is `None`. [2](#0-1) 

This means that if the Python `iris` pipeline ever returns a response where both `error` and `iris_template` are populated for the same estimate call (e.g. a non-fatal/soft error reported alongside a partially-computed template, or any future pipeline change that attaches diagnostic errors to a still-returned template), the Rust conversion takes the "happy path": it decodes `iris_codes`/`mask_codes` from base64, computes Galois secret shares via `GaloisRingIrisCodeShare::encode_iris_code`/`encode_mask_code`, and returns `Ok(EstimateOutput{..})` — the reported error is dropped on the floor with no logging, no propagation, and no way for downstream signup/fraud logic to know the pipeline flagged a problem. This estimate output subsequently flows into iris code sharing/enrollment logic used during signup. [3](#0-2) 

The only test coverage exercises the two "clean" cases — error alone (`iris_template: None`) and template alone (`error: None`) — never the combined case, so there is no regression protection against this precedence issue. [4](#0-3) 

### Impact Explanation
This is a fail-open code path in the fail-closed error-handling model for iris biometric extraction. If a legitimate or attacker-influenced pipeline state ever produces both fields set, biometric data (iris template, code/mask shares) derived from a run the pipeline itself flagged as erroneous would be accepted and used for signup/enrollment as if it were fully valid, undermining the integrity guarantee that only pipeline-validated iris data is used for identity binding/uniqueness checks. This maps to a signup-integrity / identity-binding correctness impact category rather than a direct authentication bypass, since it depends on the upstream Python `iris` library's behavior, which is outside this repository.

### Likelihood Explanation
Exploitability requires the third-party Python `iris` pipeline (a dependency not present in this repo) to actually emit a response with both `error` and `iris_template` populated for the same call — the Rust code provides no independent verification that this state is impossible, so it currently relies entirely on an assumption about dependency behavior that cannot be verified from this codebase. Absent evidence that the `iris` package can produce this dual state today, this is a design/defensive-coding gap rather than a demonstrated exploitable path from camera-presented input.

### Recommendation
Change the precedence check in `TryFrom<PipelineOutput> for EstimateOutput` to check `output.error` first (or require it to be `None`) before trusting `iris_template`, e.g.:
```rust
if let Some(err) = output.error {
    return Err(err);
}
if let Some(iris_template) = output.iris_template {
    ...
} else {
    Err(PyError { ... }) // no template and no error is also unexpected
}
```
This makes error state take unconditional precedence, matching fail-closed handling regardless of dependency behavior.

### Proof of Concept
Add a test to `src/agents/python/iris/extracts.rs` constructing a Python dict literal with both `'error': {...}` and `'iris_template': {...}` populated (mirroring `EXAMPLE_IRIS_OUTPUT_WITH_ERROR` combined with `EXAMPLE_IRIS_OUTPUT`'s `iris_template`), then assert that `TryInto::<EstimateOutput>::try_into()` returns `Err` with the expected `error_type`/`message`, rather than `Ok`. Under current code, this test would fail because the conversion returns `Ok(EstimateOutput{..})`, demonstrating the silently-discarded error.

### Citations

**File:** src/agents/python/iris/types.rs (L16-23)
```rust
pub struct PipelineOutput {
    pub error: Option<PyError>,

    pub iris_template: Option<IrisTemplate>,
    pub normalized_image: Option<NormalizedIris>,
    pub normalized_image_resized: Option<NormalizedIris>,
    pub metadata: Metadata,
}
```

**File:** src/agents/python/iris/mod.rs (L99-130)
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
```

**File:** src/agents/python/iris/mod.rs (L205-220)
```rust
        let output: EstimateOutput = self
            .agent
            .call_method("estimate", (image,), Some(kwargs))?
            .extract::<PipelineOutput>()?
            .try_into()?;

        log_iris_data(
            &output.iris_code_shares,
            &output.mask_code_shares,
            &output.iris_code,
            &output.mask_code,
            &output.iris_code_version,
            left_eye,
            "iris agent",
        );
        Ok(output)
```

**File:** src/agents/python/iris/extracts.rs (L37-105)
```rust
    const EXAMPLE_IRIS_OUTPUT_WITH_ERROR: &str = r#"{
    'error': {'error_type': 'VectorizationError',
              'message': 'Geometry raster verification failed.',
              'traceback': '  File '
                 '"/home/worldcoin/venv/lib/python3.8/site-packages/iris/pipelines/iris_pipeline.py", '
                 'line 104, in run\n'
                 '    _ = self.nodes[node.name](**input_kwargs)\n'
                 '  File '
                 '"/home/worldcoin/venv/lib/python3.8/site-packages/iris/io/class_configs.py", '
                 'line 58, in __call__\n'
                 '    return self.execute(*args, **kwargs)\n'
                 '  File '
                 '"/home/worldcoin/venv/lib/python3.8/site-packages/iris/io/class_configs.py", '
                 'line 69, in execute\n'
                 '    result = self.run(*args, **kwargs)\n'
                 '  File '
                 '"/home/worldcoin/venv/lib/python3.8/site-packages/iris/nodes/vectorization/contouring.py", '
                 'line 73, in run\n'
                 '    raise VectorizationError("Geometry raster '
                 'verification failed.")\n'},
    'iris_template': None,
    'normalized_image': None,
    'normalized_image_resized': None,
    'metadata': {'eye_centers': None,
       'eye_orientation': None,
       'eye_side': 'left',
       'image_size': (1440, 1080),
       'iris_bbox': None,
       'iris_version': '1.7.2',
       'occlusion30': None,
       'occlusion90': None,
       'ellipticity': None,
       'offgaze_score': None,
       'pupil_to_iris_property': None,
       'template_property': None}}"#;

    #[test]
    fn test_extract_normal_output() -> Result<()> {
        Python::with_gil(|py| {
            let output: EstimateOutput = py
                .eval(EXAMPLE_IRIS_OUTPUT, None, None)
                .wrap_err("eval failed")?
                .extract::<PipelineOutput>()?
                .try_into()?;
            assert!(output.iris_code.starts_with("E0zFXyJgq2+/sT"));
            assert!(output.mask_code.ends_with("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADMzP//////w=="));
            assert_eq!(output.metadata.image_size, Some((1440, 1080)));
            Ok(())
        })
    }

    #[test]
    fn test_extract_output_with_errors() -> Result<()> {
        Python::with_gil(|py| {
            let output: Result<EstimateOutput, PyError> = py
                .eval(EXAMPLE_IRIS_OUTPUT_WITH_ERROR, None, None)
                .wrap_err("eval failed")?
                .extract::<PipelineOutput>()?
                .try_into();
            match output {
                Ok(_) => panic!("Output should be an Err"),
                Err(e) => {
                    assert_eq!(e.error_type, "VectorizationError");
                    assert_eq!(e.message, "Geometry raster verification failed.");
                }
            }
            Ok(())
        })
    }
```
