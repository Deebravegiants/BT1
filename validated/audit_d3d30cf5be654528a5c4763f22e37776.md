## Title
CatFee API Key and Secret Logged in Plaintext During TRON Bandwidth Purchaser Client Initialization - (File: `tesseract/messaging/tron/src/lib.rs`)

### Summary
`TronClient::new` initializes the CatFee client (used to purchase TRON bandwidth/energy before submitting transactions) and logs the entire `CatFeeConfig` struct — including the plaintext `api_key` and `api_secret` fields — at `info` level via `{:#?}` formatting.

### Finding Description
`CatFeeConfig` is defined with `#[derive(Debug, Clone)]` and contains `api_key: String` and `api_secret: String` with no redaction, masking, or custom `Debug` implementation: [1](#0-0) 

When a relayer operator configures CatFee credentials for TRON energy/bandwidth purchasing, `TronClient::new` builds this config and unconditionally logs it in full at `info` level: [2](#0-1) 

Because `CatFeeConfig`'s `Debug` output is derived (not redacted), the `{:#?}` format specifier serializes `api_key` and `api_secret` verbatim into the log line. This mirrors the root cause in GHSA-rcqj-3fmp-5cqx / CVE-2025-30677: connector configuration objects carrying credentials were logged via their default `Debug`/`toString` representation without masking, exposing plaintext secrets in application logs.

### Impact Explanation
Anyone with access to the tesseract relayer's log output (log aggregation systems, log files, CI artifacts, shared operational dashboards, or a misconfigured log sink) can recover the operator's CatFee `api_key` and `api_secret` in plaintext. These credentials authenticate HMAC-signed requests to the CatFee service that purchase TRON energy/bandwidth on behalf of the relayer's TRON account; leaking them lets an attacker forge authenticated purchase requests against the operator's CatFee account, potentially draining the account's balance or making unauthorized energy purchases billed to the operator — a direct funds-loss vector for the bandwidth-purchasing relayer operator, consistent with CWE-532 (Insertion of Sensitive Information into Log File).

### Likelihood Explanation
This code path executes automatically and deterministically on every `TronClient::new` invocation whenever `catfee_api_key`/`catfee_api_secret` are configured — there is no gating, sampling, or debug-only condition — so the secret is logged on every relayer startup as long as CatFee integration is enabled. Exploitation only requires read access to relayer logs, which in most operational setups (log shipping, cloud logging, shared debugging) is far broader than access to the underlying credential store.

### Recommendation
- Implement a custom `Debug`/`Display` for `CatFeeConfig` that masks `api_key` and `api_secret` (e.g., `***redacted***` or last-4-chars only), matching the masking pattern already used elsewhere in this codebase (see `maskSecret`/`maskToml` in the simplex filler).
- Remove or redact the `{:#?}` log statement in `TronClient::new`, logging only non-sensitive fields (e.g., `api_base`, `timeout`) or a boolean "CatFee integration enabled" flag without the config dump.

### Proof of Concept
1. Configure a TRON relayer node with `catfee_api_key` and `catfee_api_secret` set in `TronConfig`.
2. Start the relayer; `TronClient::new` executes and reaches:
```rust
log::info!(target: LOG_TARGET, "CatFee integration enabled: {:#?}", catfee_config);
```
3. Inspect the relayer's stdout/log file/log aggregator — the full `CatFeeConfig` Debug dump, including `api_key: "…"` and `api_secret: "…"` in cleartext, appears in the `info`-level log line.
4. Any party with read access to those logs now holds valid CatFee API credentials and can issue authenticated HMAC-signed requests against the CatFee service impersonating the operator.

### Citations

**File:** tesseract/messaging/tron/src/catfee.rs (L44-54)
```rust
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
