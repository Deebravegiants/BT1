### Title
CatFee API Key and Secret Are Written in Plaintext to Application Logs at Startup - (File: tesseract/messaging/tron/src/lib.rs)

### Summary
`TronClient::new` logs the entire `CatFeeConfig` struct — including the plaintext `api_key` and `api_secret` used for CatFee HMAC authentication — via `log::info!(target: LOG_TARGET, "CatFee integration enabled: {:#?}", catfee_config)`. Because `CatFeeConfig` derives `Debug` with no redaction of its credential fields, every startup of a TRON relayer/bandwidth-purchaser configured with CatFee credentials permanently writes those secrets to the process log output, exactly matching the CWE-532 bug class in the referenced advisory (NVD API key logged by DependencyCheck in debug mode) — except here it is logged unconditionally at `info` level rather than gated behind a debug flag.

### Finding Description
`CatFeeConfig` is defined with `#[derive(Debug, Clone)]` and stores the raw credential material directly as `String` fields: [1](#0-0) 

`TronClient::new` builds this config from the relayer's `TronConfig.catfee_api_key` / `catfee_api_secret` fields and immediately logs it with the `{:#?}` (pretty Debug) formatter: [2](#0-1) 

Since `Debug` is derived rather than manually implemented with masking, the pretty-printed output includes `api_key: "…"` and `api_secret: "…"` verbatim. This happens on every relayer boot whenever the operator has configured CatFee (a TRON bandwidth-purchasing integration used to fund energy for `IsmpHost` transaction submission), with no debug/trace gate — the log line is emitted at `info` level, which is commonly the default and always captured by process/log aggregation. Any log sink, log-shipping pipeline, support bundle, or shared monitoring dashboard that ingests the relayer's stdout/stderr will durably persist the plaintext CatFee credentials, allowing anyone with log access to hijack the account used to purchase TRON energy/bandwidth for the relayer's transaction submission pipeline.

### Impact Explanation
CatFee credentials authorize purchasing TRON energy/bandwidth billed to the operator's CatFee account and are tied to the relayer's TRON signing key/owner address (used for submitting ISMP messages to the `IsmpHost` contract via `tx::handle_message_submission`). Leakage lets an attacker who obtains the logs impersonate the operator against the CatFee API (e.g., drain prepaid balance, redirect energy purchases, or disrupt the relayer's ability to submit transactions by exhausting/misusing the account), and depending on account-scope, can enable unauthorized paid actions. This falls under CWE-532 and directly threatens the relayer/bandwidth-purchaser's ability to reliably deliver messages, which the validation scope treats as a route-availability risk. Because the secret is written unconditionally at `info` level (not merely in a rare debug mode), the exposure window is broader than in the original CVE analog.

### Likelihood Explanation
Likelihood is high for any operator who enables the CatFee feature: the log line fires deterministically on every `TronClient` construction (i.e., every relayer restart), requiring no attacker interaction — only that the operator's log storage/transport is not perfectly access-controlled (a very common condition, e.g., centralized logging, container log drivers, crash-report bundles shared with support).

### Recommendation
Implement a manual `Debug` (or a wrapper `Secret`/`Redacted` type) for `CatFeeConfig` that masks `api_key` and `api_secret` (e.g., print only a fixed-length placeholder or last 4 characters), and change the log statement in `TronClient::new` to avoid `{:#?}` on the raw config — log only non-sensitive fields (e.g., `api_base`, `timeout`) or the redacted form.

### Proof of Concept
1. Configure a TRON relayer node with `catfee_api_key` and `catfee_api_secret` set in `TronConfig`.
2. Start the relayer; `TronClient::new` executes: [3](#0-2) 
3. Inspect the process log output (stdout/stderr or any aggregated log sink) — the pretty-printed `CatFeeConfig` Debug output contains the plaintext `api_key` and `api_secret` values exactly as configured, because `CatFeeConfig`'s derived `Debug` does not redact them: [4](#0-3)

### Citations

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
