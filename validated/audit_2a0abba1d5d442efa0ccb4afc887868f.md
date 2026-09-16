### Title
CatFee API credentials logged in plaintext at INFO level during TronClient bandwidth-purchaser initialization - (File: `tesseract/messaging/tron/src/lib.rs`)

### Summary
`TronClient::new` logs the entire `CatFeeConfig` struct — including the plaintext `api_key` and `api_secret` used to authenticate with the CatFee bandwidth/energy-purchasing service — via `log::info!("CatFee integration enabled: {:#?}", catfee_config)`. `CatFeeConfig` derives `Debug` with no redaction, so every field, including the two secrets, is written to whatever log sink the relayer/collator process uses. This mirrors CVE-2019-10195: a batch/initialization code path that logs credentials embedded in a configuration/command object, exposing them to anyone with log access.

### Finding Description
`CatFeeConfig` is defined with a derived `Debug` implementation that exposes `api_key` and `api_secret` verbatim: [1](#0-0) 

`TronClient::new` builds this config from the operator-supplied `TronConfig.catfee_api_key` / `catfee_api_secret` and immediately logs it at `info` level using the pretty-printed `Debug` format, which serializes the secret fields in cleartext: [2](#0-1) 

This happens every time a TRON chain is configured with CatFee ("bandwidth purchaser") integration — i.e., on every relayer/collator startup or config reload for that chain — not behind any debug/trace gate, so it lands in the default log stream (and in any log-forwarding pipeline, monitoring stack, or support bundle) unconditionally. The codebase elsewhere shows the correct pattern is known and used (e.g., `maskToml`/`maskSecret` in the simplex package explicitly redacts API keys/secrets before display), which underscores that this specific code path skipped that safeguard: [3](#0-2) 

### Impact Explanation
The CatFee API key/secret authorize purchasing TRON energy/bandwidth on behalf of the relayer's TRON account and are billed against that account. An attacker who gains access to logs (log aggregation systems, crash reports, support bundles, misconfigured log storage, or any operator/monitoring role with read access to logs but not the original config file) recovers the CatFee credentials in plaintext. With them, the attacker can impersonate the relayer's CatFee client, place unauthorized energy/bandwidth purchase orders billed to the relayer's account, or exhaust/redirect the CatFee balance — draining funds intended for the relayer's TRON transaction submission (bandwidth purchaser) operations. This matches CWE-200 (Medium) exactly as in the FreeIPA advisory: log-file exposure of credentials that would otherwise never leave the config file.

### Likelihood Explanation
This is not conditional on rare misuse: the log statement fires unconditionally whenever `catfee_api_key`/`catfee_api_secret` are configured (the intended and documented way to enable CatFee), at `info` level, which most deployments do not suppress. Any standard log pipeline (systemd journal, container log driver, centralized logging/SIEM) will persist and potentially forward this secret to broader audiences than the relayer operator who owns the underlying config file.

### Recommendation
Remove or redact the `Debug`-based log statement for `CatFeeConfig`. Either implement a custom `Debug`/`Display` for `CatFeeConfig` that masks `api_key` and `api_secret` (matching the `maskSecret`/`maskToml` pattern already used elsewhere in this codebase), or log only non-sensitive fields (e.g., `api_base`, `timeout`, and a boolean "credentials provided") instead of the full struct.

### Proof of Concept
1. Configure a TRON chain in `tesseract.toml` with `catfee_api_key` and `catfee_api_secret` set.
2. Start the relayer/collator; `TronClient::new` runs and executes:
   `log::info!(target: LOG_TARGET, "CatFee integration enabled: {:#?}", catfee_config);`
3. Inspect the process's stdout/log file — the CatFee `api_key` and `api_secret` appear in plaintext, exactly as configured, because `CatFeeConfig`'s derived `Debug` impl prints every field with no masking.
4. Any party with subsequent access to that log output (log aggregator, support ticket attachment, monitoring dashboard) now has full CatFee API credentials for the relayer's account.

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

**File:** sdk/packages/simplex/src/services/server/setup-api.ts (L322-337)
```typescript
/** Display-only TOML with every secret masked; the round-trip gate runs on the real config. */
export function maskToml(config: FillerConfigFile, chainLabels?: string[]): string {
	const masked: FillerConfigFile = JSON.parse(JSON.stringify(config))
	const signer = masked.simplex.signer as Record<string, string> | undefined
	if (signer) {
		for (const field of ["key", "apiToken", "apiPrivateKey"]) {
			if (signer[field]) signer[field] = maskSecret(signer[field])
		}
	}
	if (masked.simplex.substratePrivateKey) {
		masked.simplex.substratePrivateKey = maskSecret(masked.simplex.substratePrivateKey)
	}
	if (masked.binance) {
		masked.binance.apiKey = maskSecret(masked.binance.apiKey)
		masked.binance.apiSecret = maskSecret(masked.binance.apiSecret)
	}
```
