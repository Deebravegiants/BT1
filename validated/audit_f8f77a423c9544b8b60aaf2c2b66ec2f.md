### Title
`Config::validate` performs no semantic validation of fraud/liveness-relevant fields, allowing a malicious backend config to redirect iris/IR-Net model selection - ([File: src/config.rs])

### Summary
`Config::validate` only checks `basic_config.sound_volume <= MAX_SOUND_VOLUME` and returns `true` for every other field. Fields such as `child_threshold`, `contact_lens_model_config`, `ir_net_model_configs`, and `iris_model_configs`, which are parsed directly from the untrusted backend response in `Config::from_backend`, pass through `.filter(Self::validate)` unchecked and are accepted as the live orb `Config`.

### Finding Description
`backend::config::Config` deserializes `ir_net_model_configs: Option<HashMap<String,String>>`, `iris_model_configs: Option<HashMap<String,String>>`, `contact_lens_model_config: Option<String>`, and `child_threshold: Option<f32>` straight from the backend JSON response with no constraints on the string contents or float range. [1](#0-0) 

`Config::from_backend` copies these fields verbatim into the runtime `Config` and then gates acceptance solely through `.filter(Self::validate)`. [2](#0-1) 

`Config::validate` itself only checks the sound volume bound and unconditionally returns true otherwise: [3](#0-2) 

These values are then consumed by the Python agent initializers: `ir_net.rs`'s `From<&Config> for Model` copies `ir_net_model_configs` directly into the agent's `configs` map [4](#0-3) , and `iris/mod.rs`'s `From<&Config> for Model` does the same for `iris_model_configs` [5](#0-4) . During agent `init`, the selected string is passed via `choose_config` and then handed to the Python side (`IrNet::init(py, &config)` and `IRISPipeline.load_from_config(config)`) [6](#0-5) [7](#0-6) . I was unable to fully inspect `choose_config` in `src/agents/python/mod.rs` (only its definition location was found, not its body) or the `IrNet::init`/`IRISPipeline.load_from_config` implementations in the `orb_ir_net`/`iris` Python packages, so I cannot confirm with certainty whether those layers perform their own path/content sanitization before using the string to locate a model config file or resource.

Because `Config::validate` performs no bounds/format check on `child_threshold` (e.g., negative or out-of-[0,1] values could disable or invert the under-age classifier gate) and no content check on the model-config map values/keys (e.g., empty strings, path-traversal-like strings, or an entry keyed to the running model version), a backend response that is self-contradictory or adversarial with respect to these fields will still satisfy `validate()` and become the active `Config`.

### Impact Explanation
If the downstream Python model loaders (`orb_ir_net::IrNet::init`, `iris.pipelines.iris_pipeline.IRISPipeline.load_from_config`) resolve the config string to a filesystem path or otherwise trust it without their own sanitization, a malicious/self-contradictory `ir_net_model_configs`/`iris_model_configs`/`contact_lens_model_config` value selected via `choose_config` could load an unintended or attacker-influenced model configuration, weakening liveness/occlusion/contact-lens or child-detection checks. This maps to a liveness/fraud-bypass or under-age-detection bypass impact category. However, the actual severity depends entirely on the (unverified) behavior of `choose_config` and the Python `IrNet`/`IRISPipeline` config loaders, which I could not confirm reject malformed/malicious paths.

### Likelihood Explanation
Precondition is an attacker-controlled/compromised backend config response reaching an orb (as stipulated by the prompt's precondition), which is outside normal attacker capability for an "unprivileged attacker" absent a compromised backend or MITM of an authenticated, token-signed request (`request()` uses `basic_auth` with `ORB_ID`/orb token over presumably TLS). [8](#0-7)  Given the stated precondition is accepted per the rules, the lack of semantic validation in `Config::validate` is confirmed and reproducible, but exploitability of the "weakened liveness" impact remains unconfirmed without seeing `choose_config` and the Python model-loading internals.

### Recommendation
Extend `Config::validate` to perform semantic checks on fraud/liveness-relevant fields: validate `child_threshold` is within an expected numeric range if present; validate `contact_lens_model_config`, and the keys/values of `ir_net_model_configs`/`iris_model_configs`, against an allow-list of known config identifiers (not raw filesystem paths) and reject empty strings, path separators (`/`, `\`), or `..` sequences. Ensure `choose_config` and the Python-side loaders never interpret these strings as raw filesystem paths without allow-listing.

### Proof of Concept
```rust
// src/config.rs test module
#[test]
fn validate_rejects_malicious_model_configs() {
    let mut config = Config::default();
    config.ir_net_model_configs = Some(HashMap::from([
        ("global".to_owned(), "../../etc/passwd".to_owned()),
    ]));
    config.iris_model_configs = Some(HashMap::from([
        ("global".to_owned(), String::new()),
    ]));
    config.child_threshold = Some(-5.0); // out-of-range / nonsensical
    // Expected: Config::validate should reject this config.
    assert!(!config.validate(), "validate() must reject malicious/self-contradictory model config paths and out-of-range child_threshold");
}
```
Currently this test would fail (i.e., `validate()` returns `true`) because `Config::validate` only checks `sound_volume`. [3](#0-2)

### Citations

**File:** src/backend/config.rs (L38-43)
```rust
    pub contact_lens_model_config: Option<String>,
    #[serde(flatten)]
    pub fraud_check_engine_config: fraud_check::BackendConfig,
    pub ir_net_model_configs: Option<HashMap<String, String>>,
    pub iris_model_configs: Option<HashMap<String, String>>,
    pub child_threshold: Option<f32>,
```

**File:** src/backend/config.rs (L79-90)
```rust
pub async fn request() -> Result<Response> {
    let request = super::client()?
        .get(format!("{}/api/v1/orbs/{}", *MANAGEMENT_BACKEND_URL, *ORB_ID))
        .basic_auth(&*ORB_ID, Some(get_orb_token()?));
    match request.send().await?.error_for_status() {
        Ok(response) => Ok(response.json().await?),
        Err(err) => {
            tracing::error!("Received error response {:?}", err);
            Err(err.into())
        }
    }
}
```

**File:** src/config.rs (L220-286)
```rust
            contact_lens_model_config,
            fraud_check_engine_config,
            ir_net_model_configs,
            iris_model_configs,
            child_threshold,
            face_identifier_model_configs,
            thermal_camera_pairing_status_timeout: thermal_camera_pairing_status_timeout
                .map_or(default.thermal_camera_pairing_status_timeout, Duration::from_millis),
            thermal_camera: thermal_camera.unwrap_or(default.thermal_camera),
            depth_camera: depth_camera.unwrap_or(default.depth_camera),
            self_serve: self_serve.unwrap_or(default.self_serve),
            self_serve_button: self_serve_button.unwrap_or(default.self_serve_button),
            self_serve_ask_op_qr_for_possibly_underaged:
                self_serve_ask_op_qr_for_possibly_underaged
                    .unwrap_or(default.self_serve_ask_op_qr_for_possibly_underaged),
            self_serve_ask_op_qr_for_possibly_underaged_timeout:
                self_serve_ask_op_qr_for_possibly_underaged_timeout.map_or(
                    default.self_serve_ask_op_qr_for_possibly_underaged_timeout,
                    Duration::from_millis,
                ),
            self_serve_app_skip_capture_trigger: self_serve_app_skip_capture_trigger
                .unwrap_or(default.self_serve_app_skip_capture_trigger),
            self_serve_app_capture_trigger_timeout: self_serve_app_capture_trigger_timeout
                .map_or(default.self_serve_app_capture_trigger_timeout, Duration::from_millis),
            self_serve_biometric_capture_timeout: self_serve_biometric_capture_timeout
                .map_or(default.self_serve_biometric_capture_timeout, Duration::from_millis),
            mirror_default_phi_offset_degrees: mirror_default_phi_offset_degrees
                .unwrap_or(default.mirror_default_phi_offset_degrees),
            mirror_default_theta_offset_degrees: mirror_default_theta_offset_degrees
                .unwrap_or(default.mirror_default_theta_offset_degrees),
            process_agent_logger_pruning: process_agent_logger_pruning
                .unwrap_or(default.process_agent_logger_pruning),
            backend_http_request_timeout: backend_http_request_timeout
                .map_or(default.backend_http_request_timeout, Duration::from_millis),
            backend_http_connect_timeout: backend_http_connect_timeout
                .map_or(default.backend_http_connect_timeout, Duration::from_millis),
            pcp_v3: pcp_v3.unwrap_or(default.pcp_v3),
            pcp_tier1_blocking_threshold: pcp_tier1_blocking_threshold
                .unwrap_or(default.pcp_tier1_blocking_threshold),
            pcp_tier1_dropping_threshold: pcp_tier1_dropping_threshold
                .unwrap_or(default.pcp_tier1_dropping_threshold),
            pcp_tier2_blocking_threshold: pcp_tier2_blocking_threshold
                .unwrap_or(default.pcp_tier2_blocking_threshold),
            pcp_tier2_dropping_threshold: pcp_tier2_dropping_threshold
                .unwrap_or(default.pcp_tier2_dropping_threshold),
            ignore_user_centric_signups: ignore_user_centric_signups
                .unwrap_or(default.ignore_user_centric_signups),
            user_qr_validation_use_full_operator_qr: user_qr_validation_use_full_operator_qr
                .unwrap_or(default.user_qr_validation_use_full_operator_qr),
            user_qr_validation_use_only_operator_location:
                user_qr_validation_use_only_operator_location
                    .unwrap_or(default.user_qr_validation_use_only_operator_location),
            orb_relay_shutdown_wait_for_pending_messages:
                orb_relay_shutdown_wait_for_pending_messages.map_or(
                    default.orb_relay_shutdown_wait_for_pending_messages,
                    Duration::from_millis,
                ),
            orb_relay_shutdown_wait_for_shutdown: orb_relay_shutdown_wait_for_shutdown
                .map_or(default.orb_relay_shutdown_wait_for_shutdown, Duration::from_millis),
            orb_relay_announce_orb_id_retries: orb_relay_announce_orb_id_retries
                .unwrap_or(default.orb_relay_announce_orb_id_retries),
            orb_relay_announce_orb_id_timeout: orb_relay_announce_orb_id_timeout
                .map_or(default.orb_relay_announce_orb_id_timeout, Duration::from_millis),
            operator_qr_expiration_time: operator_qr_expiration_time
                .map_or(default.operator_qr_expiration_time, Duration::from_millis),
        })
        .filter(Self::validate)
```

**File:** src/config.rs (L322-326)
```rust
    /// Validates the configuration.
    #[must_use]
    pub fn validate(&self) -> bool {
        self.basic_config.sound_volume <= MAX_SOUND_VOLUME
    }
```

**File:** src/agents/python/ir_net.rs (L203-209)
```rust
    fn init<'py>(self, py: Python<'py>) -> Result<Box<dyn super::Environment<Self> + 'py>> {
        tracing::info!("{} agent: loading model with config: {self:?}", Model::NAME);
        let t = Instant::now();

        let version = check_model_version(IrNet::module(py)?, Model::MINIMUM_MODEL_VERSION)?;
        let config = choose_config(self.configs.as_ref(), &version)?;
        let ir_net = IrNet::init(py, &config)?;
```

**File:** src/agents/python/ir_net.rs (L233-237)
```rust
impl From<&Config> for Model {
    fn from(config: &Config) -> Self {
        Self { configs: config.ir_net_model_configs.clone() }
    }
}
```

**File:** src/agents/python/iris/mod.rs (L228-241)
```rust
    fn init<'py>(self, py: Python<'py>) -> Result<Box<dyn super::Environment<Self> + 'py>> {
        tracing::info!("{} agent: loading model with config: {self:?}", Model::NAME);
        let t = Instant::now();

        let module = py.import("iris")?;
        let version = check_model_version(module, Model::MINIMUM_MODEL_VERSION)?;
        let config = choose_config(self.configs.as_ref(), &version)?;

        let module = py.import("iris.pipelines.iris_pipeline")?;
        let init: InitAgent = module
            .getattr("IRISPipeline")?
            .getattr("load_from_config")?
            .call1((config,))?
            .extract()?;
```

**File:** src/agents/python/iris/mod.rs (L267-271)
```rust
impl From<&Config> for Model {
    fn from(config: &Config) -> Self {
        Self { configs: config.iris_model_configs.clone() }
    }
}
```
