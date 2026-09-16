### Title
CatFee API secret logged in plaintext at INFO level on every TRON client startup - ([File: tesseract/messaging/tron/src/lib.rs])

### Summary
`TronClient::new` logs the entire `CatFeeConfig` struct — including the raw `api_key` and `api_secret` used for CatFee HMAC authentication — via `log::info!("CatFee integration enabled: {:#?}", catfee_config)`. This mirrors CVE-2021-3684's bug class (plaintext secret leaked into installation/operational logs), except here the leaked secret is a live bandwidth-purchasing credential rather than an image pull secret.

### Finding Description
`CatFeeConfig` derives a plain `#[derive(Debug, Clone)]` with `api_key: String` and `api_secret: String` fields and no redaction logic: [1](#0-0) 

When a TRON relayer chain is configured with `catfee_api_key`/`catfee_api_secret` in `TronConfig`, `TronClient::new` constructs the `CatFeeConfig` and immediately logs it with the `{:#?}` (pretty Debug) formatter at `info` level: [2](#0-1) 

Because `Debug` is derived (not custom/redacted), this format string serializes both `api_key` and `api_secret` in full, plaintext form into whatever log sink the relayer operator uses (stdout/docker logs, log aggregation, monitoring pipelines, crash reports, etc.). This happens on every `TronClient` construction — i.e., every relayer startup or reconnect where the TRON chain is configured with CatFee credentials — not a one-time event.

The CatFee API uses this exact key/secret pair as its sole authentication mechanism (HMAC-SHA256 keyed by `api_secret`, sent with `CF-ACCESS-KEY`/`CF-ACCESS-SIGN` headers): [3](#0-2) 

Anyone with read access to the relayer's logs (a common, lower-privilege attack surface than the machine's filesystem/root — e.g., a shared log aggregator, a monitoring dashboard, or a support ticket containing pasted logs) obtains the full credential and can independently compute valid HMAC signatures to impersonate the relayer's CatFee account.

### Impact Explanation
CatFee is used to purchase TRON energy/bandwidth to reduce TRX fees on transaction submission, and its API key/secret is the complete authentication mechanism for placing purchase orders. An attacker who recovers the leaked `api_key`/`api_secret` from logs can:
- Authenticate to CatFee as the relayer operator and place unauthorized energy purchase orders, draining the operator's CatFee account balance/funds.
- Potentially redirect or manipulate energy purchases (e.g., to different TRON addresses), disrupting the relayer's bandwidth purchasing pipeline used to keep TRON message-submission costs down, which can degrade or halt message delivery on the TRON route.

This is a direct financial/credential-theft impact tied to the "bandwidth purchaser" role explicitly in scope, reachable without any special privilege beyond log access — a materially different, and typically much lower, bar than compromising the host itself.

### Likelihood Explanation
Any relayer operator who enables CatFee integration (a supported, documented feature) will have this secret written to logs on every single node start/restart. Log exposure is common in production incident response, third-party log aggregation, dashboards, or accidental sharing (e.g., pasting logs in a bug report or Slack channel when troubleshooting an issue) — the exact scenario the analogous CVE-2021-3684 report warns about for installation logs. No attacker action is required to cause the leak; it happens automatically as part of normal operation, making the likelihood of exposure high in any environment where logs are collected or shared.

### Recommendation
Do not `Debug`-format `CatFeeConfig` (or any config type containing `api_key`/`api_secret`/`signer` fields) directly into logs. Implement a manual `Debug` impl (or a `redacted()`/masked accessor) that masks `api_key` and `api_secret`, and change the log call in `TronClient::new` to use that masked representation instead of `{:#?}` on the raw struct. Audit other `Debug`/`Serialize` derives on config structs carrying secrets (e.g., `TronConfig` itself, which flattens `EvmConfig` and could contain a `signer`) for the same issue.

### Proof of Concept
1. Configure a TRON chain with CatFee integration enabled:
```toml
[tron]
type = "evm"
tron_api_url = "https://api.trongrid.io"
catfee_api_key = "REAL_CATFEE_KEY"
catfee_api_secret = "REAL_CATFEE_SECRET"
```
2. Start the tesseract relayer (or trigger a `TronClient::new` reconnect).
3. Observe relayer stdout/log output containing:
```
CatFee integration enabled: CatFeeConfig {
    api_key: "REAL_CATFEE_KEY",
    api_secret: "REAL_CATFEE_SECRET",
    api_base: "https://api.catfee.io",
    timeout: 30s,
}
``` [2](#0-1) 
4. Any party with access to these logs now holds the full CatFee credential pair and can sign and submit authenticated requests to `https://api.catfee.io` as the relayer operator, e.g., placing energy purchase orders billed to the victim's account.

### Citations

**File:** tesseract/messaging/tron/src/catfee.rs (L21-29)
```rust
//! ## Authentication
//! CatFee requires HMAC-SHA256 signatures for all API requests:
//! - Header: CF-ACCESS-KEY (your API key)
//! - Header: CF-ACCESS-SIGN (Base64 encoded HMAC-SHA256 signature)
//! - Header: CF-ACCESS-TIMESTAMP (ISO 8601 timestamp, e.g., 2023-08-26T12:34:56.789Z)
//!
//! Signature format: `Base64(HMAC-SHA256(secret, timestamp + method + requestPath))`
//! where requestPath includes query parameters (e.g.,
//! `/v1/order?quantity=65000&receiver=ADDR&duration=1h`)
```

**File:** tesseract/messaging/tron/src/catfee.rs (L43-54)
```rust
/// Configuration for the CatFee API client
#[derive(Debug, Clone)]
pub struct CatFeeConfig {
	/// API key for authentication (required)
	pub api_key: String,
	/// API secret for HMAC signature generation (required)
	pub api_secret: String,
	/// Base URL for the CatFee API
	pub api_base: String,
	/// HTTP request timeout
	pub timeout: Duration,
}
```

**File:** tesseract/messaging/tron/src/lib.rs (L247-262)
```rust
		// Initialize CatFee client if API credentials are provided
		let catfee = if let (Some(api_key), Some(api_secret)) =
			(&config.catfee_api_key, &config.catfee_api_secret)
		{
			let catfee_config = CatFeeConfig {
				api_key: api_key.clone(),
				api_secret: api_secret.clone(),
				timeout: std::time::Duration::from_secs(config.tron_api_timeout_secs),
				..Default::default()
			};
			log::info!(target: LOG_TARGET, "CatFee integration enabled: {:#?}", catfee_config);
			Some(CatFeeClient::new(catfee_config)?)
		} else {
			log::info!(target: LOG_TARGET, "CatFee integration disabled (API credentials not provided)");
			None
		};
```
