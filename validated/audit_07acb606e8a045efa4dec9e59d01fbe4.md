### Title
Unvalidated `child_threshold` config value from backend can bypass/break underage detection - (File: src/config.rs)

### Summary
The Sherlock bug is a class of "unbounded/unvalidated configurable threshold" issue: an admin-settable threshold (`THRESHOLD`) is compared against a derived value without any bound enforcement, and because the value can be set outside a safe range, downstream security-relevant logic (deposits/withdrawals gating) behaves incorrectly for long periods. The analogous pattern in `orb-core` is `Config::child_threshold`, a backend-supplied float that is intended to gate the "possibly underaged" / self-serve age-verification flow, but which is passed straight through from the backend response into the live `Config` with no range validation at all.

### Finding Description
`Config::validate()` is the only sanity check performed on a freshly parsed/downloaded configuration, and it checks exactly one field — `sound_volume` — ignoring every other numeric/threshold field including `child_threshold`: [1](#0-0) 

`child_threshold` itself is taken as an `Option<f32>` straight from the backend JSON response and forwarded unmodified into the `Config` struct in `from_backend()`, with no `clamp`, no range assertion, and no fallback sanitization (contrast this with `sound_volume` which is explicitly `.clamp(0, MAX_SOUND_VOLUME)` and `fan_max_speed` which is explicitly `.clamp(0.0, DEFAULT_MAX_FAN_SPEED)`): [2](#0-1) [3](#0-2) 

The field is documented as the "Person Classifier config: under-age threshold" — i.e., it is the score cutoff used to flag a signup as belonging to a minor and route it into the `self_serve_ask_op_qr_for_possibly_underaged` flow rather than allowing an unsupervised self-serve signup: [4](#0-3) [5](#0-4) 

Just like the Sherlock finding — where `THRESHOLD` is admin-adjustable but not constrained to the ~2% safe band, causing the pool-vs-oracle comparison to silently misbehave for up to 24 hours — `child_threshold` is backend-adjustable but not constrained to any valid probability/score range (e.g. `[0.0, 1.0]`). If the backend pushes (accidentally, via a bad deploy, bad experiment flag, or malformed JSON default) a `child_threshold` outside the classifier's meaningful range, the underage-classification comparison against this threshold degrades exactly the same way the balancer-vs-chainlink comparison did: it can silently always evaluate true or always evaluate false, defeating the age-gating logic for every subsequent signup handled by that Orb until a corrected config is redeployed.

### Impact Explanation
If `child_threshold` is pushed outside its valid range, the person-classifier comparison against it can be forced to always classify signups as "not underaged" (or vice versa always "underaged"). In the "always not underaged" case, minors are silently allowed to complete an unsupervised self-serve signup without the operator-QR-verification safeguard that `self_serve_ask_op_qr_for_possibly_underaged` is designed to trigger — an unauthorized/misattributed signup with no fraud/liveness backstop for that specific enrollment. This maps directly to the "unauthorized signup" impact category, reachable purely by an ordinary (unprivileged) person walking up to the Orb, with no special privileges required on the user side — the root cause is entirely a missing bound-check on backend-supplied config, mirroring the Sherlock root cause 1:1.

### Likelihood Explanation
Likelihood is moderate: it requires the backend to serve an out-of-range `child_threshold` (e.g. due to a bad config push, unit mismatch, or a null/garbage float slipping through `Option<f32>` deserialization), which is plausible given there is zero server-side or client-side validation enforcing the value stays within the classifier's expected domain — the exact same failure mode that made the original THRESHOLD bug realistic (an admin/ops actor can set a bad value without any code stopping them).

### Recommendation
Add explicit bounds validation for `child_threshold` (and other threshold-like config fields) inside `Config::from_backend()`/`Config::validate()`, clamping or rejecting values outside the classifier's valid range (e.g. `[0.0, 1.0]`), mirroring the existing `clamp` pattern already used for `sound_volume` and `fan_max_speed`.

### Proof of Concept
1. Backend `orb config` endpoint response sets `"ChildThreshold": 5.0` (or any value outside the classifier's valid score domain) due to a deployment mistake.
2. `Config::from_backend()` copies this value verbatim with no clamping: [6](#0-5) .
3. `Config::validate()` does not reject this configuration because it only checks `sound_volume`: [1](#0-0) .
4. Every subsequent signup on that Orb evaluates the age-classifier score against this out-of-range threshold, causing the underage-detection comparison to degrade to a constant result, allowing unsupervised self-serve signups for underaged persons to bypass the `self_serve_ask_op_qr_for_possibly_underaged` safeguard.

### Citations

**File:** src/config.rs (L75-76)
```rust
    /// Person Classifier config: under-age threshold.
    pub child_threshold: Option<f32>,
```

**File:** src/config.rs (L90-93)
```rust
    /// Ask the operator for a QR code when a possibly underaged person is detected.
    pub self_serve_ask_op_qr_for_possibly_underaged: bool,
    /// How long to wait for the operator to scan the QR code when a possibly underaged person is detected.
    pub self_serve_ask_op_qr_for_possibly_underaged_timeout: Duration,
```

**File:** src/config.rs (L204-224)
```rust
        Some(Self {
            basic_config: BasicConfig {
                sound_volume: sound_volume.clamp(0, MAX_SOUND_VOLUME),
                language,
            },
            operation_country: operation_country.or(default.operation_country),
            operation_city: operation_city.or(default.operation_city),
            fan_max_speed: Some(
                fan_max_speed.unwrap_or(DEFAULT_MAX_FAN_SPEED).clamp(0.0, DEFAULT_MAX_FAN_SPEED),
            ),
            slow_internet_ping_threshold: slow_internet_ping_threshold
                .map_or(default.slow_internet_ping_threshold, Duration::from_millis),
            block_signup_when_no_internet,
            ir_eye_save_fps_override,
            ir_face_save_fps_override,
            thermal_save_fps_override,
            contact_lens_model_config,
            fraud_check_engine_config,
            ir_net_model_configs,
            iris_model_configs,
            child_threshold,
```

**File:** src/config.rs (L322-327)
```rust
    /// Validates the configuration.
    #[must_use]
    pub fn validate(&self) -> bool {
        self.basic_config.sound_volume <= MAX_SOUND_VOLUME
    }

```

**File:** src/backend/config.rs (L26-43)
```rust
pub struct Config {
    pub sound_volume: u64,
    pub language: Option<String>,
    pub operation_country: Option<String>,
    pub operation_city: Option<String>,
    pub fan_max_speed: Option<f32>,
    pub slow_internet_ping_threshold: Option<u64>,
    #[serde(default)]
    pub block_signup_when_no_internet: bool,
    pub ir_eye_save_fps_override: Option<f32>,
    pub ir_face_save_fps_override: Option<f32>,
    pub thermal_save_fps_override: Option<f32>,
    pub contact_lens_model_config: Option<String>,
    #[serde(flatten)]
    pub fraud_check_engine_config: fraud_check::BackendConfig,
    pub ir_net_model_configs: Option<HashMap<String, String>>,
    pub iris_model_configs: Option<HashMap<String, String>>,
    pub child_threshold: Option<f32>,
```
